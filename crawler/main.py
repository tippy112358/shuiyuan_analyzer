import logging
import mysql.connector
from crawler import Crawler
import os

def main():
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 数据库连接
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='shuiyuan'
    )
    
    try:
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
        
        # 使用新的爬取函数（这里只爬取前2页作为示例）
        crawler.topic_and_posts_crawler(10000)
        
    except Exception as e:
        logging.error(f"爬虫运行错误: {e}")
    finally:
        crawler.close()

if __name__ == "__main__":
    main() 