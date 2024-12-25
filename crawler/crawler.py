import logging
import time
from typing import Dict, List
import requests
from mysql.connector import MySQLConnection
from mysql.connector.aio import MySQLConnectionAbstract
from requests.cookies import RequestsCookieJar
import json
import os
from pathlib import Path

from database import DatabaseManager
from parser import DataParser

class Crawler:
    """爬虫主类"""
    def __init__(self, conn: MySQLConnectionAbstract, cookie_file: str = 'cookies.json',request_interval_seconds: float = 0.5):
        self.headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://shuiyuan.sjtu.edu.cn/',
        }
        self.cookies = RequestsCookieJar()
        self.cookie_file = Path(cookie_file)
        self.delay = request_interval_seconds
        self.db = DatabaseManager(conn)
        self.parser = DataParser()
        self.logger = logging.getLogger(__name__)
        
        # 尝试加载保存的cookie
        self._load_cookies()
        
        # 添加缓存文件路径
        self.cache_dir = Path('cache')
        self.cache_dir.mkdir(exist_ok=True)
        self.processed_users_file = self.cache_dir / 'processed_users.json'
        self.processed_topics_file = self.cache_dir / 'processed_topics.json'
        
        # 初始化缓存集合
        self.processed_users = self._load_cache(self.processed_users_file)
        self.processed_topics = self._load_cache(self.processed_topics_file)

    def _save_cookies(self) -> None:
        """保存cookies到文件"""
        try:
            cookie_dict = {cookie.name: cookie.value for cookie in self.cookies}
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_dict, f, indent=2)
            # self.logger.info(f"Cookies saved to {self.cookie_file}")
        except Exception as e:
            self.logger.error(f"Error saving cookies: {e}")

    def _load_cookies(self) -> None:
        """从文件加载cookies"""
        if not self.cookie_file.exists():
            return
            
        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookie_dict = json.load(f)
            
            for name, value in cookie_dict.items():
                self.cookies.set(name, value)
            
            # self.logger.info(f"Cookies loaded from {self.cookie_file}")
        except Exception as e:
            self.logger.error(f"Error loading cookies: {e}")

    def set_cookie(self, cookie_str: str) -> None:
        """从字符串设置初始Cookie"""
        if not cookie_str:
            raise ValueError("Cookie string cannot be empty")
            
        # 解析cookie字符串
        cookie_pairs = cookie_str.split(';')
        for pair in cookie_pairs:
            if '=' in pair:
                name, value = pair.strip().split('=', 1)
                self.cookies.set(name, value)

    def _update_cookies(self, response: requests.Response) -> None:
        """从响应更新cookies"""
        new_cookies = response.cookies
        updated = False
        
        for cookie in new_cookies:
            self.cookies.set(cookie.name, cookie.value, 
                           domain=cookie.domain,
                           path=cookie.path,
                           expires=cookie.expires)
            updated = True
        
        # 如果有更新，保存到文件
        if updated:
            # self.logger.info("Cookies updated from response")
            self._save_cookies()

    def _fetch_data(self, url: str, max_retries: int = 3) -> Dict:
        """获取URL数据并更新cookies，支持重试"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, cookies=self.cookies)
                
                # 如果遇到频率限制
                if response.status_code == 429:

                    retry_after = 2 * (attempt + 1)  # 递增等待时间
                    self.logger.warning(f"Rate limited, waiting {retry_after} seconds before retry")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                
                # 更新cookies
                self._update_cookies(response)
                
                return response.json()
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 * (attempt + 1)
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"Error fetching data from {url}: {e}")
                    if hasattr(response, 'text'):
                        self.logger.error(f"Response text: {response.text[:200]}...")
                    raise

    def get_current_cookies(self) -> str:
        """获取当前的cookie字符串"""
        return '; '.join([f'{cookie.name}={cookie.value}' 
                         for cookie in self.cookies])

    def check_cookie_validity(self) -> bool:
        """检查cookie是否有效"""
        try:
            # 尝试访问需要登录的页面
            test_url = 'https://shuiyuan.sjtu.edu.cn/session/current.json'
            response = requests.get(test_url, headers=self.headers, cookies=self.cookies)
            data = response.json()
            
            # 更新cookies
            self._update_cookies(response)
            
            # 检查返回的数据是否表明已登录
            return data.get('current_user') is not None
        except Exception as e:
            self.logger.error(f"Error checking cookie validity: {e}")
            return False

    def refresh_cookie_if_needed(self) -> bool:
        """如果需要，刷新cookie"""
        if not self.check_cookie_validity():
            self.logger.warning("Cookie is invalid or expired")
            return False
        return True

    def topic_and_posts_crawler(self, page_num: int) -> None:
        """爬取最新话题及��所有帖子"""
        try:
            if not self.refresh_cookie_if_needed():
                raise ValueError("Invalid or expired cookie")
                
            for page in range(page_num):
                data = self._fetch_data(
                    f'https://shuiyuan.sjtu.edu.cn/latest.json?no_definitions=true&page={page}'
                )
                
                # 处理用户数据
                self._process_users(data['users'])
                
                # 处理话题数据并获取话题ID
                topics = data['topic_list']['topics']
                total_topics = len(topics)
                
                self.logger.info(f"Processing page {page}, found {total_topics} topics")
                
                for i, topic in enumerate(topics, 1):
                    try:
                        topic_id = topic['id']
                        if topic_id in self.processed_topics:
                            continue
                            
                        # 处理话题数据
                        topic_data = self.parser.parse_topic(topic)
                        self.db.add_topic(topic_data)
                        
                        # 爬取该话题的所有帖子
                        self.logger.info(f"Processing topic {i}/{total_topics} on page {page} (ID: {topic_id})")
                        self.posts_crawler_all(topic_id)
                        
                        # 添加到已处理集合并保存
                        self.processed_topics.add(topic_id)
                        self._save_cache(self.processed_topics, self.processed_topics_file)
                        
                        # 每个话题处理完后等待
                        time.sleep(self.delay)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing topic {topic.get('id')}: {e}")
                        continue
                
                time.sleep(self.delay)
                
        except Exception as e:
            self.logger.error(f"Error in topic and posts crawler: {e}")
            raise

    def _process_users(self, users: List[Dict]) -> None:
        """处理用户数据，跳过已处理的用户"""
        for user in users:
            try:
                user_id = user['id']
                if user_id in self.processed_users:
                    continue
                    
                user_data = self.parser.parse_user(user)
                self.db.add_user(user_data)
                

                
            except Exception as e:
                self.logger.error(f"Error processing user {user.get('id')}: {e}")

    def _process_topics(self, topics: List[Dict]) -> None:
        """处理话题数据"""
        for topic in topics:
            try:
                topic_data = self.parser.parse_topic(topic)
                self.db.add_topic(topic_data)
            except Exception as e:
                self.logger.error(f"Error processing topic {topic.get('id')}: {e}")

    def posts_crawler_all(self, topic_id: int, posts_requests_num: int = 20) -> None:
        """爬取所有帖子"""
        try:
            if not self.refresh_cookie_if_needed():
                raise ValueError("Invalid or expired cookie")
                
            topic_data = self._fetch_data(
                f'https://shuiyuan.sjtu.edu.cn/t/{topic_id}.json?track_visit=false&forceLoad=true'
            )
            
            self._process_posts(topic_data['post_stream']['posts'])
            
            stream = topic_data['post_stream']['stream']
            self._process_post_stream(topic_id, stream, posts_requests_num)
            
        except Exception as e:
            self.logger.error(f"Error crawling posts for topic {topic_id}: {e}")
            raise

    def _process_post_stream(self, topic_id: int, stream: List[int], batch_size: int) -> None:
        """处理帖子流"""
        total_batches = (len(stream) + batch_size - 1) // batch_size  # 计算总批次数
        
        for i in range(0, len(stream), batch_size):
            batch = stream[i:i + batch_size]
            current_batch = i // batch_size + 1
            
            post_url = self._build_posts_url(topic_id, batch)
            
            try:
                self.logger.info(f"Processing batch {current_batch}/{total_batches} for topic {topic_id}")
                posts_data = self._fetch_data(post_url)
                self._process_posts(posts_data['post_stream']['posts'], log_progress=False)
                # 增加请求间隔
                time.sleep(self.delay/2)  # 帖子批量请求使用更长的延迟
            except Exception as e:
                self.logger.error(f"Error processing batch {current_batch}/{total_batches} for topic {topic_id}: {e}")
                # 发生错误时增加额外等待时间
                time.sleep(self.delay)

    def _build_posts_url(self, topic_id: int, post_ids: List[int]) -> str:
        """构建帖子URL"""
        post_params = "&".join(f"post_ids[]={pid}" for pid in post_ids)
        return f"https://shuiyuan.sjtu.edu.cn/t/{topic_id}/posts.json?{post_params}&include_suggested=false"

    def _process_posts(self, posts: List[Dict], log_progress: bool = True) -> None:
        """处理帖子数据，并获取每个帖子作者的详细信息"""
        total_posts = len(posts)
        
        for i, post in enumerate(posts, 1):
            try:
                # 处理帖子数据
                post_data = self.parser.parse_post(post)
                self.db.add_post(post_data)
                
                # 获取并处理用户详细信息
                topic_id = post['topic_id']
                user_id = post['user_id']
                username = post['username']
                trust_level = post.get('trust_level', 0)
                if (not user_id in self.processed_users):
                    self._fetch_and_process_user_detail(topic_id, user_id, username, trust_level)
                    self.processed_users.add(user_id)
                    self._save_cache(self.processed_users, self.processed_users_file)

                
                # 添加短暂延迟避免请求过快
                time.sleep(self.delay/2)
                
            except Exception as e:
                self.logger.error(f"Error processing post {post.get('id')}: {e}")

    def _fetch_and_process_user_detail(self, topic_id: int, user_id: int, username: str, trust_level: int) -> None:
        """获取并处理用户详细信息"""
        try:
            # URL编码用户名
            encoded_username = requests.utils.quote(username)

            # 获取用户卡片信息
            card_url = f'https://shuiyuan.sjtu.edu.cn/u/{encoded_username}/card.json?include_post_count_for={topic_id}'
            self.headers['Referer'] = f'https://shuiyuan.sjtu.edu.cn/t/{topic_id}'
            user_data = self._fetch_data(card_url)

            if 'user' in user_data:
                user_info = user_data['user']
                
                # 构建用户基本数据，添加cakedate
                user_detail = (
                    int(user_info['id']),
                    user_info['username'],
                    user_info.get('name', ''),
                    trust_level,
                    user_info.get('profile_hidden', False),
                    user_info.get('title', ''),
                    (user_info.get('cakedate', '') if user_info.get('cakedate', '') !='' else '1970-01-01')  # 添加cakedate字段
                )
                # 存储用户基本信息
                self.db.add_user(user_detail)
                # 如果用户资料未隐藏，获取详细统计信息
                if not user_info.get('profile_hidden', False):
                    summary_url = f'https://shuiyuan.sjtu.edu.cn/u/{encoded_username}/summary.json'
                    summary_data = self._fetch_data(summary_url)
                    
                    if 'user_summary' in summary_data:
                        summary = summary_data['user_summary']
                        
                        # 构建用户统计数据
                        user_summary = (

                            summary.get('likes_given', 0),
                            summary.get('likes_received', 0),
                            summary.get('topics_entered', 0),
                            summary.get('posts_read_count', 0),
                            summary.get('days_visited', 0),
                            summary.get('topic_count', 0),
                            summary.get('post_count', 0),
                            summary.get('time_read', 0),
                            summary.get('recent_time_read', 0),
                            summary.get('continuous_days_visited', 0),
                            summary.get('solved_count', 0),
                            json.dumps(summary['top_categories']),
                            user_info['id']  # user_id
                        )
                        
                        # 存储用户统计信息
                        self.db.add_user_summary(user_summary)
                
            else:
                self.logger.warning(f"No user data found for username {username}")
                
        except Exception as e:
            self.logger.error(f"Error fetching user detail for user {username}: {e}")
            self.logger.error(f"Failed URL: {card_url}")




    def close(self) -> None:
        """关闭爬虫"""
        self.db.close()

    def export_interaction_data(self, output_file: str = 'interaction_data.json') -> None:
        """导出互动数据"""
        self.db.export_interaction_data(output_file) 

    def _load_cache(self, cache_file: Path) -> set:
        """从文件加载缓存"""
        try:
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    return set(json.load(f))
            return set()
        except Exception as e:
            self.logger.error(f"Error loading cache from {cache_file}: {e}")
            return set()

    def _save_cache(self, cache_set: set, cache_file: Path) -> None:
        """保存缓存到文件"""
        try:
            with open(cache_file, 'w') as f:
                json.dump(list(cache_set), f)
        except Exception as e:
            self.logger.error(f"Error saving cache to {cache_file}: {e}") 