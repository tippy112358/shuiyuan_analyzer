import json

from bs4 import BeautifulSoup
import requests
import os
import time
import mysql.connector
from mysql.connector import Error
import datetime
new_cursor = None

class TopicCrawler:
    def __init__(self,conn):
        self.headers={
            'Connection': 'keep-alive',
            'Cookie' : '_ga=GA1.3.548267712.1730210206; _ga_LT5KXLNGWY=GS1.3.1730210206.1.1.1730210325.0.0.0; cookieconsent_status=dismiss; 10.119.9.71:80=22632.59461.21071.0000; _t=TO34MOO3KP9YkD8kXfUNJS8%2Br%2Bg1LLYr3t2i7IE5rDNmmq%2FnGfsLR4kysOZ%2FlK%2B4nqpjbHCwmeTly%2FE1mos2JK0DLqlNiOY6ljztZ0LPpgW1Yj%2BXMNZtwt4JD89c9GR7FWCI1Ou6call4%2FfGxIr%2BuRa3OmBbCYnmcQM%2Ff%2BGk1BEKHgiXA6xywngJcSNDu5NSaUZWyNrgkQCaI6BPdXVZ6d3xD9Q4CdH9zgjdmWI8sTStrj5gdOyYCI341XXIgNdxDTcA%2BzSTBzebyzIGrQM76xcczI01i%2BWLGBTFUosqk%2Bk6sl60gR6U9Q4jbvkVNMaACfCzOQ%2FAKq%2BhL1BcmRW2jEk1mls%3D--vOlkesdvk%2Bj8utl9--Trcp4LFdNcuCVBvoHyG2hg%3D%3D; _bypass_cache=true; authentication_data=%7B%22authenticated%22%3Atrue%2C%22awaiting_activation%22%3Afalse%2C%22awaiting_approval%22%3Afalse%2C%22not_allowed_from_ip_address%22%3Afalse%2C%22admin_not_allowed_from_ip_address%22%3Afalse%2C%22destination_url%22%3A%22%2F%22%7D; _forum_session=HUVW62s%2BeRgk7gbmRvHAOL6MYRaEiDmw0XJfdR4tRo6bgX9lCK5KLGzQ1SYNjg9M0viAjEO2nn2MaHkdOIVfI9P3YY37mD%2BTjyAX6FFMQWY6oDqcxVGoBSCo11Zyxslp3A4kEhfi1N2eImTMXRSjUDZKoqCK%2FztetmZXzQXvRtmmi9hJXkvaFj94E6Si%2BkCg%2Fm%2B9Wql560k4cML8jC%2FC6nEQTVT1%2FC0JUPdKbziWMjZ7miammnOQoaEhFYRDJ3zh9XKXYAohZOMq39Wsvm%2BmhJDIvw3hzQ%3D%3D--SAy%2BS%2BvQEeFzTuef--mTPKmtHyde9zGyBcGB48dQ%3D%3D',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
        }
        self.model={'post_id':'int unsigned',
                    'title':'varchar',
                    'created_at':'datetime',
                    'last_posted_at':'datetime',
                    'posts_count':'int unsigned',

                    }
        self.conn=conn
        self.cursor = conn.cursor()
        self.topic_sql=(
            """
                Call ADDTOPIC(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        )
        # self.user_insert_sql=(
        #     """
        #     INSERT INTO shuiyuan.`User`
        #     (id, username, name, trust_level)
        #     VALUES(%s, %s, %s, %s) ON DUPLICATE KEY UPDATE trust_level=2;
        #     """
        # )
        self.user_insert_sql=(
            """
            CALL ADDUSER(%s, %s, %s, %s)
            """
        )

    def set_cookie(self,cookie):
        self.headers['Cookie'] = cookie.strip()

    def crawler(self,page_num):
        url='https://shuiyuan.sjtu.edu.cn/'
        get=requests.get(url,headers=self.headers)
        for i in range(0,page_num):
            page=requests.get(f'https://shuiyuan.sjtu.edu.cn/latest.json?no_definitions=true&page={i}',headers=self.headers)
            page_content=json.loads(page.content)
            # add users
            users=page_content['users']
            for user in users:
                data=(
                    int(user['id']),
                    user['username'],
                    user['name'],
                    int(user['trust_level']),
                )
                self.user_insert(data)

            # add topics
            topic_list = page_content['topic_list']
            topics=topic_list['topics']
            for topic in topics:
                post_id=topic['id']
                title=topic['title']
                created_at=topic['created_at']
                created_at= datetime.datetime.fromisoformat(created_at[0:19])
                last_posted_at=topic['last_posted_at']
                last_posted_at = datetime.datetime.fromisoformat(last_posted_at[0:19])
                posts_count=topic['posts_count']
                reply_count=topic['reply_count']
                views=topic['views']
                like_count=topic['like_count']
                has_accepted_answer=topic['has_accepted_answer']
                pinned=topic['pinned']
                created_by=topic['posters'][0]['user_id']
                print(created_by)
                tags_tmp=topic['tags']
                tags=""
                for tag in tags_tmp:
                    tags+=tag.strip()+","
                update_timestamp=time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
                datas=(
                    post_id,
                    title,
                    created_at,
                    last_posted_at,
                    posts_count,
                    reply_count,
                    views,
                    like_count,
                    has_accepted_answer,
                    pinned,
                    created_by,
                    tags,
                    update_timestamp,
                )
                self.topic_insert(datas)
            time.sleep(0.5)

    def user_insert(self,data):
        print(data)
        self.cursor.execute(self.user_insert_sql,data)
        self.conn.commit()
        pass

    def topic_insert(self, datas):
        self.cursor.execute(self.topic_sql, datas)
        self.conn.commit()
        pass


class PostCrawler:
    def __init__(self):
        pass


# os.makedirs('./data/test/',exist_ok=True)
# with open('./data/test/shuiyuan.html','wb') as f:
#     f.write(get.content)
#
# print(get.content)
new_conn = mysql.connector.connect(
    host='localhost',  # 数据库主机地址
    user='root',  # 数据库用户名
    password='123456',  # 数据库密码
    database='shuiyuan' # 数据库名称
)
cookie=input("please input your cookie:")
tc=TopicCrawler(new_conn)
tc.set_cookie(cookie)
tc.crawler(500)
new_conn.close()