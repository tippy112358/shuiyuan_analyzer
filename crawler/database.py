import logging
from typing import Dict, List, Tuple, Optional
import mysql.connector
from mysql.connector import Error, MySQLConnection
from mysql.connector.aio import MySQLConnectionAbstract
from datetime import datetime


class DatabaseManager:
    """数据库管理类，处理所有数据库操作"""
    def __init__(self, conn: MySQLConnectionAbstract):
        self.conn = conn
        self.cursor = conn.cursor(dictionary=True)  # 使用字典游标，便于获取列名
        self.logger = logging.getLogger(__name__)
        self._init_sql_statements()
        
    def _init_sql_statements(self):
        """初始化SQL语句"""
        # 存储过程
        self.topic_sql = "CALL ADDTOPIC(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.user_sql = "CALL ADDUSER(%s, %s, %s, %s)"
        self.post_sql = "CALL ADDPOST(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        # 查询语句
        self.select_user = """
            SELECT id, username, name, trust_level 
            FROM User 
            WHERE id = %s
        """
        
        self.select_topic = """
            SELECT id, title, created_at, last_posted_at, posts_count, 
                   reply_count, views, like_count, has_accepted_answer, 
                   pinned, created_by, tags, update_timestamp
            FROM Topic 
            WHERE id = %s
        """
        
        self.select_post = """
            SELECT p.*, tp.topic_id, tp.post_number, tp.reply_to_post_number
            FROM Post p
            LEFT JOIN TopicPost tp ON p.id = tp.post_id
            WHERE p.id = %s
        """
        
        self.select_topic_posts = """
            SELECT p.*, tp.post_number, tp.reply_to_post_number
            FROM Post p
            JOIN TopicPost tp ON p.id = tp.post_id
            WHERE tp.topic_id = %s
            ORDER BY tp.post_number
        """
        
        self.select_latest_topics = """
            SELECT id, title, created_at, last_posted_at, posts_count, 
                   reply_count, views, like_count, has_accepted_answer, 
                   pinned, created_by, tags, update_timestamp
            FROM Topic 
            ORDER BY last_posted_at DESC
            LIMIT %s
        """

    def execute_procedure(self, sql: str, params: Tuple) -> None:
        """执行存储过程"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
        except Error as e:
            self.conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise

    def add_user(self, user_data: Tuple) -> None:
        """添加用户数据"""
        self.execute_procedure(self.user_sql, user_data)

    def add_topic(self, topic_data: Tuple) -> None:
        """添加话题数据"""
        self.execute_procedure(self.topic_sql, topic_data)

    def add_post(self, post_data: Tuple) -> None:
        """添加帖子数据"""
        self.execute_procedure(self.post_sql, post_data)

    def get_user(self, user_id: int) -> Optional[Dict]:
        """获取用户信息"""
        try:
            self.cursor.execute(self.select_user, (user_id,))
            return self.cursor.fetchone()
        except Error as e:
            self.logger.error(f"Error fetching user {user_id}: {e}")
            return None

    def get_topic(self, topic_id: int) -> Optional[Dict]:
        """获取话题信息"""
        try:
            self.cursor.execute(self.select_topic, (topic_id,))
            return self.cursor.fetchone()
        except Error as e:
            self.logger.error(f"Error fetching topic {topic_id}: {e}")
            return None

    def get_post(self, post_id: int) -> Optional[Dict]:
        """获取帖子信息"""
        try:
            self.cursor.execute(self.select_post, (post_id,))
            return self.cursor.fetchone()
        except Error as e:
            self.logger.error(f"Error fetching post {post_id}: {e}")
            return None

    def get_topic_posts(self, topic_id: int) -> List[Dict]:
        """获取话题的所有帖子"""
        try:
            self.cursor.execute(self.select_topic_posts, (topic_id,))
            return self.cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error fetching posts for topic {topic_id}: {e}")
            return []

    def get_latest_topics(self, limit: int = 50) -> List[Dict]:
        """获取最新话题列表"""
        try:
            self.cursor.execute(self.select_latest_topics, (limit,))
            return self.cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error fetching latest topics: {e}")
            return []

    def close(self):
        """关闭数据库连接"""
        self.cursor.close()
        self.conn.close() 