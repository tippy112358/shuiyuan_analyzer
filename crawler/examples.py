import logging
import mysql.connector
from typing import Optional, Dict, List
from datetime import datetime, timedelta

from database import DatabaseManager
from crawler import Crawler

class ShuiyuanExample:
    """水源论坛数据操作示例类"""
    def __init__(self):
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 初始化数据库连接
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',
            database='shuiyuan'
        )
        
        self.db = DatabaseManager(self.conn)
        self.crawler = None  # 爬虫实例将在需要时初始化

    def init_crawler(self, cookie: str) -> None:
        """初始化爬虫"""
        self.crawler = Crawler(self.conn)
        self.crawler.set_cookie(cookie)
        self.crawler.set_delay_time(0.5)

    def crawl_latest_topics(self, page_num: int = 50) -> None:
        """爬取最新���题示例"""
        if not self.crawler:
            raise ValueError("Crawler not initialized. Call init_crawler first.")
        
        try:
            self.logger.info(f"开始爬取最新{page_num}页话题")
            self.crawler.topic_crawler_newest(page_num)
            self.logger.info("话题爬取完成")
        except Exception as e:
            self.logger.error(f"爬取话题失败: {e}")

    def crawl_topic_posts(self, topic_id: int) -> None:
        """爬取指定话题的所有帖子示例"""
        if not self.crawler:
            raise ValueError("Crawler not initialized. Call init_crawler first.")
        
        try:
            self.logger.info(f"开始爬取话题 {topic_id} 的帖子")
            self.crawler.posts_crawler_all(topic_id)
            self.logger.info(f"话题 {topic_id} 的帖子爬取完成")
        except Exception as e:
            self.logger.error(f"爬取帖子失败: {e}")

    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """获取用户信息示例"""
        user = self.db.get_user(user_id)
        if user:
            self.logger.info(f"用户信息: {user}")
        else:
            self.logger.warning(f"未找到用户 {user_id}")
        return user

    def get_user_topics(self, user_id: int, limit: int = 10) -> List[Dict]:
        """获取用户最新发布的话题示例"""
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM Topic 
                WHERE created_by = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (user_id, limit))
            topics = cursor.fetchall()
            cursor.close()
            return topics
        except Exception as e:
            self.logger.error(f"获取用户话题失败: {e}")
            return []

    def get_topic_with_posts(self, topic_id: int) -> Dict:
        """获取话题及其所有帖子示例"""
        result = {
            'topic': None,
            'posts': [],
            'user_info': {}
        }
        
        # 获取话题信息
        topic = self.db.get_topic(topic_id)
        if not topic:
            self.logger.warning(f"未找到话题 {topic_id}")
            return result
        
        result['topic'] = topic
        
        # 获取所有帖子
        posts = self.db.get_topic_posts(topic_id)
        result['posts'] = posts
        
        # 获取相关用户信息
        user_ids = {topic['created_by']}
        for post in posts:
            user_ids.add(post['user_id'])
        
        # 获��所有相关用户信息
        for user_id in user_ids:
            user = self.db.get_user(user_id)
            if user:
                result['user_info'][user_id] = user
                
        return result

    def analyze_user_activity(self, user_id: int, days: int = 30) -> Dict:
        """分析用户活动示例"""
        try:
            cursor = self.conn.cursor(dictionary=True)
            start_date = datetime.now() - timedelta(days=days)
            
            # 获取发帖统计
            cursor.execute("""
                SELECT COUNT(*) as post_count,
                       COUNT(DISTINCT tp.topic_id) as topic_count
                FROM Post p
                JOIN TopicPost tp ON p.id = tp.post_id
                WHERE p.user_id = %s AND p.created_at > %s
            """, (user_id, start_date))
            
            stats = cursor.fetchone()
            cursor.close()
            
            return {
                'user_id': user_id,
                'period_days': days,
                'post_count': stats['post_count'],
                'topic_count': stats['topic_count'],
                'avg_posts_per_day': stats['post_count'] / days
            }
        except Exception as e:
            self.logger.error(f"分析用户活动失败: {e}")
            return {}

    def close(self):
        """关闭连接"""
        if self.crawler:
            self.crawler.close()
        self.db.close()

def main():
    """使用示例"""
    example = ShuiyuanExample()
    
    try:
        # 初始化爬虫
        cookie = input("请输入你的cookie: ")
        example.init_crawler(cookie)
        
        # 爬取数据示例
        example.crawl_latest_topics(5)  # 爬取最新5页话题
        
        # 获取某个话题的详细信息
        topic_data = example.get_topic_with_posts(12345)
        if topic_data['topic']:
            print(f"话题标题: {topic_data['topic']['title']}")
            print(f"帖子数量: {len(topic_data['posts'])}")
        
        # 分析用户活动
        user_activity = example.analyze_user_activity(67890, days=7)
        print(f"用户7天活动统计: {user_activity}")
        
    except Exception as e:
        logging.error(f"运行示例时出错: {e}")
    finally:
        example.close()

if __name__ == "__main__":
    main() 