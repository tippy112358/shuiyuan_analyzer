# Shuiyuan_analyzer

水源社区数据分析工具，包含爬虫和数据分析功能。

## 功能特点

- 爬取水源社区话题和帖子数据
- 解析并存储用户、话题、帖子信息
- 提供数据查询和分析接口
- 支持增量更新数据

## 环境要求

- Python 3.7+
- MySQL 8.0.40+
- 必要的Python包：
  - mysql-connector-python
  - requests
  - beautifulsoup4
  - lxml

## 安装说明

1. 克隆仓库
```bash
git clone https://github.com/yourusername/shuiyuan_analyzer.git
cd shuiyuan_analyzer
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

## 快速开始

1. 初始化数据库
```bash
# 创建数据库（必须使用UTF8-mb4字符集）
mysql -u root -p
CREATE DATABASE shuiyuan CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

# 导入数据库结构
mysql -u root -p shuiyuan < shuiyuan.sql
```

2. 配置数据库连接
```python
# 在代码中修改数据库连接信息
conn = mysql.connector.connect(
    host='localhost',     # 数据库主机地址
    user='root',         # 数据库用户名
    password='123456',   # 数据库密码
    database='shuiyuan'  # 数据库名称
)
```

3. 运行示例程序
```bash
# 爬取最新话题
python main.py

# 运行完整示例
python examples.py
```

## 主要模块

### Crawler（爬虫模块）
- 爬取最新话题列表
- 爬取指定话题的所有帖子
- 支持自定义爬取延迟
- 自动处理Cookie认证

### Parser（解析模块）
- 解析话题数据
- 解析帖子内容
- 清理HTML标签
- 提取纯文本内容

### DatabaseManager（数据库模块）
- 管理数据库连接
- 提供数据增删改查接口
- 支持批量操作
- 错误处理和日志记录

## 使用示例

```python
from examples import ShuiyuanExample

# 初始化
example = ShuiyuanExample()
cookie = "your_cookie_here"
example.init_crawler(cookie)

# 爬取最新话题
example.crawl_latest_topics(5)  # 爬取最新5页

# 爬取指定话题的所有帖子
example.crawl_topic_posts(12345)  # 爬取话题ID为12345的所有帖子

# 获取话题详情
topic_data = example.get_topic_with_posts(12345)
print(f"话题标题: {topic_data['topic']['title']}")
print(f"帖子数量: {len(topic_data['posts'])}")

# 分析用户活动
activity = example.analyze_user_activity(67890, days=7)
print(f"用户7天活动统计: {activity}")

# 关闭连接
example.close()
```

## 常见问题

### 1. 字符集错误
错误信息：`Incorrect string value '\xFO\x9F\xA6\xA2\xE5lx90...'`

解决方案：
- 确保数据库使用 UTF8-mb4 字符集
- 检查数据库连接字符集设置
- 确保所有表和字段都使用 UTF8-mb4 字符集

### 2. Cookie 相关问题
- Cookie 必须是有效的登录状态
- 定期更新 Cookie 以保持登录状态
- 避免频繁请求导致 Cookie 失效

## 项目结构

```
shuiyuan_analyzer/
├── crawler.py      # 爬虫实现
├── parser.py       # 内容解析器
├── database.py     # 数据库操作
├── examples.py     # 使用示例
├── main.py         # 主程序入口
└── shuiyuan.sql    # 数据库结构
```

## 开发指南

要参与本项目开发：

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 错误处理

项目包含全面的错误处理机制：
- 网络连接错误
- 数据库操作错误
- 内容解析错误
- 认证错误

## 性能考虑

- 使用数据库连接池
- 实现大数据集的批处理
- 优化爬取过程的内存使用
- 提供增量更新能力

## 注意事项

1. 请遵守水源社区的使用规则
2. 合理设置爬取延迟，避免对服务器造成压力
3. 定期备份重要数据
4. 及时更新 Cookie 保持登录状态

## 开源协议

MIT License

## 致谢

- 感谢水源社区
- 基于 Python 和 MySQL 构建
- 源于社区数据分析需求的启发

## 联系方式

如有问题和反馈，请在 GitHub 仓库中创建 Issue