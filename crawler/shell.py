import sys
import mysql.connector
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta

from database import DatabaseManager
from PyQt5.QtWidgets import *
from mysql.connector.aio import MySQLConnectionAbstract
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont
import json
from crawler import Crawler
import logging


class ShuiyuanGUI(QMainWindow):
    def __init__(self,conn=None, crawler=None):
        super().__init__()
        self.crawler = crawler
        self.example = None
        self.init_ui()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.conn = conn
        # 初始化数据库连接
    def init_ui(self):
        self.setWindowTitle('水源论坛爬虫')
        self.setGeometry(100, 100, 800, 600)
        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        # 创建标签页
        tabs = QTabWidget()
        layout.addWidget(tabs)
        # 初始化标签页
        tabs.addTab(self.create_connection_tab(), '连接设置')
        tabs.addTab(self.create_crawler_tab(), '爬虫控制')
        tabs.addTab(self.create_query_tab(), '数据查询')
        tabs.addTab(self.create_analysis_tab(), '数据分析')
        # 添加状态栏
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()
    def create_connection_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        # Cookie输入组
        cookie_group = QGroupBox('Cookie设置')
        cookie_layout = QVBoxLayout()
        load_cookie_btn = QPushButton("重新加载Cookie文件")
        cookie_layout.addWidget(load_cookie_btn)
        load_cookie_btn.clicked.connect(self.connect_to_forum)
        cookie_group.setLayout(cookie_layout)
        layout.addWidget(cookie_group)
        # 状态显示
        self.connection_status = QLabel('未连接')
        layout.addWidget(self.connection_status)
        layout.addStretch()
        return widget
    def create_crawler_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 最新话题爬取组
        latest_group = QGroupBox('爬取最新话题')
        latest_layout = QHBoxLayout()
        self.page_num_spin = QSpinBox()
        self.page_num_spin.setRange(1, 100)
        self.page_num_spin.setValue(5)
        latest_layout.addWidget(QLabel('页数:'))
        latest_layout.addWidget(self.page_num_spin)
        crawl_latest_btn = QPushButton('开始爬取')
        crawl_latest_btn.clicked.connect(self.crawl_latest_topics)
        latest_layout.addWidget(crawl_latest_btn)
        latest_group.setLayout(latest_layout)
        layout.addWidget(latest_group)
        # 指定话题爬取组
        topic_group = QGroupBox('爬取指定话题')
        topic_layout = QHBoxLayout()
        self.topic_id_input = QLineEdit()
        self.topic_id_input.setPlaceholderText('输入话题ID')
        topic_layout.addWidget(self.topic_id_input)
        crawl_topic_btn = QPushButton('爬取话题')
        crawl_topic_btn.clicked.connect(self.crawl_topic_posts)
        topic_layout.addWidget(crawl_topic_btn)
        topic_group.setLayout(topic_layout)
        layout.addWidget(topic_group)
        # 日志显示
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        return widget
    def create_query_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 话题查询组
        topic_query_group = QGroupBox('话题查询')
        topic_query_layout = QHBoxLayout()

        self.query_topic_id = QLineEdit()
        self.query_topic_id.setPlaceholderText('输入话题ID')
        topic_query_layout.addWidget(self.query_topic_id)

        query_topic_btn = QPushButton('查询')
        query_topic_btn.clicked.connect(self.query_topic)
        topic_query_layout.addWidget(query_topic_btn)

        topic_query_group.setLayout(topic_query_layout)
        layout.addWidget(topic_query_group)

        # 查询结果显示
        self.query_result = QTextEdit()
        self.query_result.setReadOnly(True)
        layout.addWidget(self.query_result)

        return widget

    def create_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        # 用户活动分析组
        analysis_group = QGroupBox('用户活动分析')
        analysis_layout = QHBoxLayout()
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText('输入用户ID')
        analysis_layout.addWidget(self.user_id_input)
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(7)
        analysis_layout.addWidget(QLabel('天数:'))
        analysis_layout.addWidget(self.days_spin)
        analyze_btn = QPushButton('分析')
        analyze_btn.clicked.connect(self.analyze_user)
        analysis_layout.addWidget(analyze_btn)
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        # 分析结果显示
        self.analysis_result = QTextEdit()
        self.analysis_result.setReadOnly(True)
        layout.addWidget(self.analysis_result)
        return widget
    def connect_to_forum(self):
        return
    def crawl_latest_topics(self):
        self.Crawl_latest_topics(self.page_num_spin.value())
        return
    def query_topic(self):
        self.get_topic_with_posts(int(self.topic_id_input.text()))
        return
    def analyze_user(self):
        self.analyze_user_activity(int(self.user_id_input.text()),self.days_spin.value())
        return
    def Crawl_latest_topics(self, page_num: int = 50) -> None:
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
        topic_id=int(self.topic_id_input.text())
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
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',
            database='shuiyuan'
        )


        crawler = Crawler(conn, cookie_file='cookies.json', request_interval_seconds=0.01)

        # 检查cookie有效性
        if crawler.check_cookie_validity():
            print("使用已保存的cookie")
        else:
            cookie = input("已保存的cookie无效，请输入新的cookie: ")
            crawler.set_cookie(cookie)

            if not crawler.check_cookie_validity():
                print("Cookie无效或已过期，请检查输入")
                return
        app = QApplication(sys.argv)
        gui = ShuiyuanGUI(crawler=crawler,conn=conn)
        gui.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
        logging.error(f"爬虫运行错误: {e}")
    finally:
        crawler.close()


if __name__ == '__main__':
    main()