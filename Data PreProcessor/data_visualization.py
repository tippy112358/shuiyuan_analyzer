import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取CSV文件为DataFrame
df = pd.read_csv('filtered_users.csv')

# 为每一列绘制频数图并计算中位数
for column in df.columns:
    # 绘制频数图
    plt.figure(figsize=(8, 6))
    df[column].plot(kind='hist', bins=30, edgecolor='black')
    plt.title(f'Frequency Distribution of {column}')
    plt.xlabel(column)
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()

    # 绘制对数变换后的频数图
    if column != "trust_level":
        plt.figure(figsize=(8, 6))
        # 对数据进行对数变换，+1是为了避免对0取对数
        np.log1p(df[column]).plot(kind='hist', bins=30, edgecolor='black')
        plt.title(f'Frequency Distribution of {column} (Log Transformed)')
        plt.xlabel(f'log1p({column})')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.show()

    # 计算并打印中位数
    median_value = df[column].median()
    print(f"The median of {column} is {median_value}")
