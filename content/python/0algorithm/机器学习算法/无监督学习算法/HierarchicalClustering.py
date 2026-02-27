#层次聚类
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram, cut_tree
from sklearn.datasets import make_blobs

# 生成一些示例数据
data, _ = make_blobs(n_samples=300, centers=3, cluster_std=0.60, random_state=0)

# 使用层次聚类算法进行聚类
linkage_matrix = linkage(data, method='ward')

# 绘制树状图（树状图可用于选择合适的聚类数）
dendrogram(linkage_matrix)
plt.title('Hierarchical Clustering Dendrogram')
plt.show()

# 根据树状图选择合适的聚类数，并进行聚类
num_clusters = 3  # 从树状图中选择的聚类数
labels = np.array([cut for cut in cut_tree(linkage_matrix, n_clusters=num_clusters)])

# 绘制结果
plt.scatter(data[:, 0], data[:, 1], c=labels.flatten(), cmap='viridis', edgecolor='k')
plt.title('Hierarchical Clustering')
plt.show()
