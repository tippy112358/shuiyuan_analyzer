import pandas as pd
import json

# 读取JSON文件
with open('user.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 提取用户数据
users = data.get("User", [])

# 转换为DataFrame
df = pd.DataFrame(users)

# 过滤掉hidden == 1的项目
df = df[df['hidden'] != 1 & df['hidden'].notnull()]

# 过滤掉time_read == 0或time_read为null的项目
df = df[df['time_read'].notnull() & (df['time_read'] != 0)]

# 保留所需的列
columns_to_keep = [
    'id', 'trust_level', 'likes_given', 'likes_received', 'topic_count',
    'post_count', 'topics_entered', 'posts_read_count', 'days_visited',
    'time_read', 'recent_time_read'
]
df = df[columns_to_keep]

# 重置索引以便使用新ID
df.reset_index(drop=True, inplace=True)

# 建立旧ID到新ID的映射（索引作为新ID）
old_to_new_id = pd.Series(df.index, index=df['id']).to_dict()

# 建立新ID到旧ID的映射
new_to_old_id = pd.Series(df['id'].values, index=df.index).to_dict()

# 保存为CSV文件，不包括旧ID
df.drop(columns=['id'], inplace=True)
df.to_csv('filtered_users.csv', index=False, encoding='utf-8')

# 保存旧ID到新ID的映射为CSV文件
old_to_new_df = pd.DataFrame(list(old_to_new_id.items()), columns=['old_id', 'new_id'])
old_to_new_df.to_csv('old_to_new_id_mapping.csv', index=False, encoding='utf-8')

# 保存新ID到旧ID的映射为CSV文件
new_to_old_df = pd.DataFrame(list(new_to_old_id.items()), columns=['new_id', 'old_id'])
new_to_old_df.to_csv('new_to_old_id_mapping.csv', index=False, encoding='utf-8')

print("Data has been filtered and saved to 'filtered_users.csv'.")
print("Old to new ID mapping saved to 'old_to_new_id_mapping.csv'.")
print("New to old ID mapping saved to 'new_to_old_id_mapping.csv'.")

# 读取comments.json文件
with open('comments.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 提取数据部分（注意：这里的键是复杂的SQL查询，因此我们直接获取它的值）
comments_data = list(data.values())[0]

# 转换为DataFrame
df_comments = pd.DataFrame(comments_data)

# 读取旧ID到新ID的映射
id_mapping_df = pd.read_csv('old_to_new_id_mapping.csv')
old_to_new_id = pd.Series(id_mapping_df['new_id'].values, index=id_mapping_df['old_id']).to_dict()

# 保留所需的列
df_comments = df_comments[['post_user_id', 'topic_user_id']]

# 替换post_user_id和topic_user_id中的old_id为new_id
df_comments['post_user_id'] = df_comments['post_user_id'].map(old_to_new_id)
df_comments['topic_user_id'] = df_comments['topic_user_id'].map(old_to_new_id)

# 删除任何一个ID不存在于映射中的行
df_comments.dropna(subset=['post_user_id', 'topic_user_id'], inplace=True)

# 将new_id转换为整数类型
df_comments['post_user_id'] = df_comments['post_user_id'].astype(int)
df_comments['topic_user_id'] = df_comments['topic_user_id'].astype(int)

#自环/重边处理
# 删除post_user_id等于topic_user_id的行
df_comments = df_comments[df_comments['post_user_id'] != df_comments['topic_user_id']]

# 删除重复行
df_comments.drop_duplicates(inplace=True)

# 保存处理后的DataFrame为CSV
df_comments.to_csv('processed_comments.csv', index=False, encoding='utf-8')

print("Processed comments data has been saved to 'processed_comments.csv'.")