from datetime import datetime
from typing import Dict, Tuple
from bs4 import BeautifulSoup
import re

class DataParser:
    """数据解析类，处理所有数据解析操作"""
    @staticmethod
    def parse_user(user: Dict) -> Tuple:
        """解析用户数据"""
        return (
            int(user['id']),
            user['username'],
            user.get('name', ''),
            user.get('trust_level', 0),  # 默认trust_level为0
            user.get('profile_hidden', False),
            user.get('title', ''),
            user.get('cakedate', '1970-01-01')  # 添加cakedate字段
        )

    @staticmethod
    def parse_topic(topic: Dict) -> Tuple:
        """解析话题数据"""
        created_at = datetime.fromisoformat(topic['created_at'][0:19])
        last_posted_at = datetime.fromisoformat(topic['last_posted_at'][0:19])
        tags = ",".join(tag.strip() for tag in topic['tags'])
        
        return (
            topic['id'],
            topic['title'],
            created_at,
            last_posted_at,
            topic['posts_count'],
            topic['reply_count'],
            topic['views'],
            topic['like_count'],
            topic['has_accepted_answer'],
            topic['pinned'],
            topic['posters'][0]['user_id'],
            tags,
            datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        )

    @staticmethod
    def parse_post(post: Dict) -> Tuple:
        """解析帖子数据"""
        created_at = datetime.fromisoformat(post['created_at'][0:19])
        updated_at = datetime.fromisoformat(post['updated_at'][0:19])
        
        # 解析帖子内容
        content = DataParser.parse_post_content(post['cooked'])

        return (
            post['id'],
            content,
            post['user_id'],
            post['reads'],
            created_at,
            updated_at,
            post['post_type'],
            post['score'],
            post['version'],
            post['quote_count'],
            post['topic_id'],
            post['post_number'],
            post['reply_to_post_number']
        )

    @staticmethod
    def parse_post_content(html_content: str) -> str:
        """解析帖子HTML内容，只保留纯文本"""
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 移除不需要的标签及其内容
        for tag in soup.find_all(['script', 'style', 'code', 'pre']):
            tag.decompose()
            
        # 移除引用块
        for quote in soup.find_all('aside', class_='quote'):
            quote.decompose()
            
        # 移除表情图片
        for emoji in soup.find_all('img', class_='emoji'):
            emoji.decompose()
            
        # 移除上传的图片
        for upload in soup.find_all('div', class_='lightbox-wrapper'):
            upload.decompose()
            
        # 移除所有链接，保留链接文本
        for link in soup.find_all('a'):
            if link.string:
                link.replace_with(link.string)
            else:
                link.decompose()
                
        # 获取纯文本内容
        text = soup.get_text(separator=' ', strip=True)
        
        # 清理特殊字符和多余的空白
        text = re.sub(r'[\n\r\t]+', ' ', text)  # 替换换行、回车、制表符为空格
        text = re.sub(r'\s+', ' ', text)  # 合并多个空格
        text = re.sub(r'[^\w\s\u4e00-\u9fff,.!?，。！？、]', '', text)  # 只保留中英文字符、数字、基本标点
        
        return text.strip()

    @staticmethod
    def extract_mentions(content: str) -> list:
        """提取帖子中的@提及"""
        mentions = re.findall(r'@(\w+)', content)
        return list(set(mentions))

    @staticmethod
    def extract_urls(content: str) -> list:
        """提取帖子中的URL"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content)
        return list(set(urls)) 