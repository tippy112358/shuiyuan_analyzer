import logging
import time
from typing import Dict, List
import requests
from mysql.connector import MySQLConnection
from mysql.connector.aio import MySQLConnectionAbstract

from database import DatabaseManager
from parser import DataParser

class Crawler:
    """爬虫主类"""
    def __init__(self, conn: MySQLConnectionAbstract):
        self.headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.delay = 0.5
        self.db = DatabaseManager(conn)
        self.parser = DataParser()
        self.logger = logging.getLogger(__name__)

    def set_cookie(self, user_cookie: str) -> None:
        """设置Cookie"""
        self.headers['Cookie'] = user_cookie.strip()

    def set_delay_time(self, delay: float) -> None:
        """设置请求延迟"""
        self.delay = delay

    def _fetch_data(self, url: str) -> Dict:
        """获取URL数据"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching data from {url}: {e}")
            raise

    def topic_crawler_newest(self, page_num: int) -> None:
        """爬取最新话题"""
        try:
            for page in range(page_num):
                self.logger.info(f"Crawling page {page}")
                data = self._fetch_data(
                    f'https://shuiyuan.sjtu.edu.cn/latest.json?no_definitions=true&page={page}'
                )
                
                self._process_users(data['users'])
                self._process_topics(data['topic_list']['topics'])
                
                time.sleep(self.delay)
        except Exception as e:
            self.logger.error(f"Error in topic crawler: {e}")
            raise

    def _process_users(self, users: List[Dict]) -> None:
        """处理用户数据"""
        for user in users:
            try:
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

    def posts_crawler_all(self, topic_id: int, posts_requests_num: int = 6) -> None:
        """爬取所有帖子"""
        try:
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
        for i in range(0, len(stream), batch_size):
            batch = stream[i:i + batch_size]
            post_url = self._build_posts_url(topic_id, batch)
            
            try:
                posts_data = self._fetch_data(post_url)
                self._process_posts(posts_data['post_stream']['posts'])
                time.sleep(self.delay)
            except Exception as e:
                self.logger.error(f"Error processing post batch {i}-{i+batch_size}: {e}")

    def _build_posts_url(self, topic_id: int, post_ids: List[int]) -> str:
        """构建帖子URL"""
        post_params = "&".join(f"post_ids[]={pid}" for pid in post_ids)
        return f"https://shuiyuan.sjtu.edu.cn/t/{topic_id}/posts.json?{post_params}&include_suggested=false"

    def _process_posts(self, posts: List[Dict]) -> None:
        """处理帖子数据"""
        for post in posts:
            try:
                post_data = self.parser.parse_post(post)
                self.db.add_post(post_data)
            except Exception as e:
                self.logger.error(f"Error processing post {post.get('id')}: {e}")

    def close(self) -> None:
        """关闭爬虫"""
        self.db.close() 