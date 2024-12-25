import pandas as pd
import numpy as np
from torch_geometric.data.data import Data
import torch

# 读取CSV文件
filtered_users = pd.read_csv('filtered_users.csv')
processed_comments = pd.read_csv('processed_comments.csv')

# 生成x数组，去掉filtered_users中的trust_level列
#x = filtered_users.drop(columns=['trust_level']).to_numpy()
x = filtered_users.drop(columns=['post_count']).to_numpy()

# 生成edge_index数组，保留processed_comments中的所有值
edge_index = processed_comments.to_numpy().T  # 转置使其形状为[2, num_edge]

# 生成y数组，根据trust_level的条件
#y = (filtered_users['trust_level'] > 1).astype(int).to_numpy()
#y = filtered_users['trust_level'].astype(int).to_numpy()
y = (filtered_users['post_count'] > 5).astype(int).to_numpy()

# 生成train_mask, val_mask, test_mask
num_users = len(filtered_users)
train_end = int(num_users * 0.7)
val_end = int(num_users * 0.9)

train_mask = np.zeros(num_users, dtype=bool)
val_mask = np.zeros(num_users, dtype=bool)
test_mask = np.zeros(num_users, dtype=bool)

train_mask[:train_end] = True
val_mask[train_end:val_end] = True
test_mask[val_end:] = True

# 打印一些信息以验证结果
print(f"x shape: {x.shape}")
print(f"edge_index shape: {edge_index.shape}")
print(f"y shape: {y.shape}")
print(f"train_mask: {train_mask.sum()} True values")
print(f"val_mask: {val_mask.sum()} True values")
print(f"test_mask: {test_mask.sum()} True values")

# Exist GPU Acceleration ?
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

x = torch.tensor(x).to(device.__str__()).to(torch.float32)
y = torch.tensor(y).to(device.__str__()).to(torch.int64)
edge_index = torch.tensor(edge_index).to(device.__str__()).to(torch.int64)
train_mask = torch.tensor(train_mask).to(device.__str__())
val_mask = torch.tensor(val_mask).to(device.__str__())
test_mask = torch.tensor(val_mask).to(device.__str__())

data = Data(x=x,y=y,edge_index=edge_index,train_mask=train_mask,val_mask=val_mask,test_mask=test_mask)
print(data)
print(data.x)
print(data.y)
print(data.edge_index)
print(data.train_mask)

num_node_features = 9
num_classes = 2

import torch
import torch.nn.functional as nnFun
from torch_geometric.nn import GCNConv
from torch_geometric.datasets import Planetoid
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_fscore_support
import networkx as nx

class GCN(torch.nn.Module):

    def __init__(self, features, hidden_dimension, classes):
        super(GCN, self).__init__()
        # 输入的节点特征维度 * 中间隐藏层的维度
        self.conv1 = GCNConv(features, hidden_dimension)
        # 中间隐藏层的维度 * 节点类别
        self.conv2 = GCNConv(hidden_dimension, classes)

    def forward(self, data):
        # 节点特征 和 邻接关系
        x, edge_index = data.x, data.edge_index
        # 传入卷积层一
        x = self.conv1(x, edge_index)
        # 激活函数
        x = nnFun.relu(x)
        # dropout层 —— 防止过拟合
        x = nnFun.dropout(x, training=self.training)
        # 传入卷积层二
        x = self.conv2(x, edge_index)
        # 使用 softmax 得到概率分布
        return nnFun.log_softmax(x, dim=1)
    
def plot_metrics(precisions, recalls, f1s, losses):
    """
    训练指标变化过程可视化
    :param precisions:
    :param recalls:
    :param f1s:
    :param losses:
    :return:
    """
    epochs = range(1, len(precisions) + 1)
    plt.figure(figsize=(10, 8))
    plt.plot(epochs, precisions, 'g', label='Precision')
    plt.plot(epochs, recalls, 'r', label='Recall')
    plt.plot(epochs, f1s, 'm', label='F1')
    #plt.plot(epochs, losses, 'b', label='Loss')
    plt.title('Training And Validation Metrics')
    plt.xlabel('Epochs')
    plt.ylabel('Metrics')
    plt.legend()
    plt.show()

# 构建模型
hidden_dimension = 16  # 中间隐藏层维度为 16
gcn_model = GCN(num_node_features, hidden_dimension, num_classes).to(device)

# 定义优化函数
learn_rate = 0.01  # 学习率
weight_decay = 5e-4  # 控制权重衰减的强度
optimizer = torch.optim.Adam(gcn_model.parameters(), lr=learn_rate, weight_decay=weight_decay)

# 进入模型训练模式（启用 Dropout 和 Batch Normalization 防止过拟合）
precisions, recalls, f1s, losses = [], [], [], []
gcn_model.train()
for epoch in range(200):
    # 清空梯度（避免由反向传播导致的梯度累加）
    optimizer.zero_grad()
    # 模型输出
    out = gcn_model(data)
    # 计算负对数似然损失
    loss = nnFun.nll_loss(out[data.train_mask], data.y[data.train_mask])
    losses.append(loss.item())
    # 反向传播计算梯度
    loss.backward()
    # 一步优化
    optimizer.step()
    # 在验证集上计算指标
    #  精确度 precision_val: 预测为正类的样本中，真正为正类的比例 True Positive / (True Positive + False Positive)
    #  召回率 recall_val: 所有真实正类中被正确预测为正类的比例 True Positive / (True Positive + False Negative)
    #  F1 值 f1_val: 精确率和召回率的加权平均值
    gcn_model.eval()
    _, predicted_val = torch.max(out[data.val_mask], dim=1)
    precision_val, recall_val, f1_val, _ = \
        precision_recall_fscore_support(data.y[data.val_mask].cpu(), predicted_val.cpu(), average='macro')
    precisions.append(precision_val)
    recalls.append(recall_val)
    f1s.append(f1_val)
    # 计算负对数似然损失
    print("precision_val: %f, recall_val: %f, f1_val: %f, loss: %f" % (precision_val, recall_val, f1_val, loss.item()))
    gcn_model.train()
# 训练过程参数变化可视化
plot_metrics(precisions, recalls, f1s, losses)

def plot_result_graph(indices, edge_index, pred):
    """
    结果图可视化
    :param indices:
    :param edge_index:
    :param pred:
    :return:
    """
    # 创建无向图
    G = nx.Graph()

    # 加入节点
    for i in indices:
        G.add_node(i.item())

    for j in range(edge_index.shape[1]):
        src, tgt = edge_index[0][j].item(), edge_index[1][j].item()
        if src in test_indices and tgt in test_indices:
            G.add_edge(src, tgt)

    # 获取节点分类结果
    test_predictions = pred[test_indices]
    # 创建节点颜色列表，根据分类结果设置不同的颜色
    node_colors = test_predictions.tolist()
    # 设置布局算法
    pos = nx.spring_layout(G)
    # 绘图
    nx.draw(G, pos,
            with_labels=False,
            node_size=20,
            node_color=node_colors,
            cmap='Set1',
            style="solid",
            width=1.0)
    plt.show()
# 进入模型评估模式
gcn_model.eval()
_, predicted_val = gcn_model(data).max(dim=1)  # 得到模型输出的类别
num_correct = int(predicted_val[data.test_mask].eq(data.y[data.test_mask]).sum().item())  # 计算正确的个数
num_mask = int(data.test_mask.sum())
print('测试集数量: {:d}, 正确预测数量: {:d}: 最终评估状态下测试集精确度: {:.4f}'.format(num_mask, num_correct, num_correct / num_mask))

# 结果图可视化
test_indices = data.test_mask.nonzero(as_tuple=False).view(-1)
plot_result_graph(test_indices, data.edge_index, predicted_val)