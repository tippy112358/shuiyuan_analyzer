# Shuiyuan_analyzer

## Part1：crawler

### Environment

python

mysql 8.0.40

### Necessary Requirement：

A valid cookie for shuiyuan community 

### Easy Start

1. Using `shuiyuan.sql` to initialize MySQL database

2. Modify the setting of MySQL connection in `shuiyuan.py`

   ```python
   new_conn = mysql.connector.connect(
       host='localhost',  # 数据库主机地址
       user='root',  # 数据库用户名
       password='123456',  # 数据库密码
       database='shuiyuan' # 数据库名称
   )
   ```

3. Run `python shuiyuan.py` to start crawling the topics data from shuiyuan

4. Enter your own cookie while visiting shuiyuan.

