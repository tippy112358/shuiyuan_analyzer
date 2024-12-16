# Shuiyuan_analyzer

A data analysis tool for ShuiYuan Community (SJTU), featuring crawler and data analysis functionalities.

## Features

- Crawl topics and posts from ShuiYuan Community
- Parse and store user, topic, and post information
- Provide data query and analysis interfaces
- Support incremental data updates

## Requirements

- Python 3.7+
- MySQL 8.0.40+
- Required Python packages:
  - mysql-connector-python
  - requests
  - beautifulsoup4
  - lxml

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/shuiyuan_analyzer.git
cd shuiyuan_analyzer
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

## Quick Start

1. Initialize Database
```bash
# Create database (Must use UTF8-mb4 character set)
mysql -u root -p
CREATE DATABASE shuiyuan CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

# Import database structure
mysql -u root -p shuiyuan < shuiyuan.sql
```

2. Configure Database Connection
```python
# Modify database connection settings in code
conn = mysql.connector.connect(
    host='localhost',     # Database host
    user='root',         # Database username
    password='123456',   # Database password
    database='shuiyuan'  # Database name
)
```

3. Run Example Programs
```bash
# Crawl latest topics
python main.py

# Run complete examples
python examples.py
```

## Core Modules

### Crawler Module
- Fetch latest topic list
- Crawl all posts for specific topics
- Support customizable crawling delay
- Handle Cookie authentication automatically

### Parser Module
- Parse topic data
- Parse post content
- Clean HTML tags
- Extract plain text content

### DatabaseManager Module
- Manage database connections
- Provide CRUD operations
- Support batch operations
- Error handling and logging

## Usage Examples

```python
from examples import ShuiyuanExample

# Initialize
example = ShuiyuanExample()
cookie = "your_cookie_here"
example.init_crawler(cookie)

# Crawl latest topics
example.crawl_latest_topics(5)  # Crawl latest 5 pages

# Crawl all posts for a specific topic
example.crawl_topic_posts(12345)  # Crawl all posts for topic ID 12345

# Get topic details
topic_data = example.get_topic_with_posts(12345)
print(f"Topic title: {topic_data['topic']['title']}")
print(f"Number of posts: {len(topic_data['posts'])}")

# Analyze user activity
activity = example.analyze_user_activity(67890, days=7)
print(f"User 7-day activity stats: {activity}")

# Close connections
example.close()
```

## Common Issues

### 1. Character Set Error
Error message: `Incorrect string value '\xFO\x9F\xA6\xA2\xE5lx90...'`

Solutions:
- Ensure database uses UTF8-mb4 character set
- Check database connection character set settings
- Verify all tables and fields use UTF8-mb4 character set

### 2. Cookie Issues
- Cookie must be in valid login state
- Update Cookie periodically to maintain login status
- Avoid frequent requests that might invalidate Cookie

## Important Notes

1. Please comply with ShuiYuan Community usage rules
2. Set reasonable crawling delays to avoid server stress
3. Backup important data regularly
4. Update Cookie timely to maintain login status

## Project Structure

```
shuiyuan_analyzer/
├── crawler.py      # Crawler implementation
├── parser.py       # Content parser
├── database.py     # Database operations
├── examples.py     # Usage examples
├── main.py         # Main entry point
└── shuiyuan.sql    # Database structure
```

## Development

To contribute to this project:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Error Handling

The project includes comprehensive error handling:
- Network connection errors
- Database operation errors
- Content parsing errors
- Authentication errors

## Performance Considerations

- Uses connection pooling for database operations
- Implements batch processing for large datasets
- Optimizes memory usage during crawling
- Provides incremental update capabilities

## License

MIT License

## Acknowledgments

- Thanks to the ShuiYuan Community
- Built with Python and MySQL
- Inspired by community needs for data analysis

## Contact

For questions and feedback, please open an issue in the GitHub repository.

