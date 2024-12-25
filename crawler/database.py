import logging
from typing import Dict, List, Tuple, Optional
import mysql.connector
from mysql.connector import Error, MySQLConnection
from mysql.connector.aio import MySQLConnectionAbstract
from datetime import datetime
import json


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
        self.user_sql = "CALL ADDUSER(%s, %s, %s, %s, %s, %s, %s)"  # id, username, name, trust_level, hidden, title, cakedate
        self.post_sql = "CALL ADDPOST(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # 添加用户统计信息存储过程
        self.user_summary_sql = """
            UPDATE User 
            SET 
                likes_given = %s,
                likes_received = %s,
                topics_entered = %s,
                posts_read_count = %s,
                days_visited = %s,
                topic_count = %s,
                post_count = %s,
                time_read = %s,
                recent_time_read = %s,
                continuous_days_visited = %s,
                solved_count = %s,
                top_categories = %s
            WHERE id = %s;
        """
        
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

    def export_interaction_data(self, output_file: str = 'interaction_data.json') -> None:
        """导出互动数据为JSON格式"""
        try:
            # 获取所有 topic_posts 记录
            self.cursor.execute("""
                SELECT tp.post_id, tp.topic_id, tp.post_number, tp.reply_to_post_number
                FROM TopicPost tp
            """)
            topic_posts = self.cursor.fetchall()
            
            interaction_data = []
            
            for record in topic_posts:
                post_id = record['post_id']
                topic_id = record['topic_id']
                reply_to_post_number = record['reply_to_post_number']
                
                # 获取发帖用户ID
                self.cursor.execute("""
                    SELECT user_id 
                    FROM Post 
                    WHERE id = %s
                """, (post_id,))
                post_result = self.cursor.fetchone()
                if not post_result:
                    continue
                post_user_id = post_result['user_id']
                
                # 获取话题创建者ID
                self.cursor.execute("""
                    SELECT created_by 
                    FROM Topic 
                    WHERE id = %s
                """, (topic_id,))
                topic_result = self.cursor.fetchone()
                if not topic_result:
                    continue
                topic_user_id = topic_result['created_by']
                
                # 获取被回复帖子的作者ID（如果存在）
                reply_to_post_user_id = None
                if reply_to_post_number:
                    self.cursor.execute("""
                        SELECT p.user_id
                        FROM TopicPost tp
                        JOIN Post p ON tp.post_id = p.id
                        WHERE tp.topic_id = %s AND tp.post_number = %s
                    """, (topic_id, reply_to_post_number))
                    reply_result = self.cursor.fetchone()
                    if reply_result:
                        reply_to_post_user_id = reply_result['user_id']
                
                # 构建数据记录
                interaction_record = {
                    'post_id': post_id,
                    'topic_id': topic_id,
                    'post_number': record['post_number'],
                    'reply_to_post_number': reply_to_post_number,
                    'post_user_id': post_user_id,
                    'topic_user_id': topic_user_id,
                    'reply_to_post_user_id': reply_to_post_user_id
                }
                
                interaction_data.append(interaction_record)
            
            # 写入JSON文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(interaction_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Successfully exported {len(interaction_data)} records to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error exporting interaction data: {e}")
            raise 

    def add_user_summary(self, user_summary_data: Tuple) -> None:
        """添加用户统计数据"""
        # 需要两次传递相同的参数，因为SQL语句中有UPDATE和INSERT
        params = user_summary_data  # 添加user_id用于WHERE条件
        self.execute_procedure(self.user_summary_sql, params) 