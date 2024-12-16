import logging
import mysql.connector
from crawler import Crawler

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
        crawler = Crawler(conn)
        cookie = input("请输入你的cookie: ")
        crawler.set_cookie(cookie)
        
        # 爬取最新话题
        crawler.posts_crawler_all(332055)
        
    except Exception as e:
        logging.error(f"爬虫运行错误: {e}")
    finally:
        crawler.close()

if __name__ == "__main__":
    main() 