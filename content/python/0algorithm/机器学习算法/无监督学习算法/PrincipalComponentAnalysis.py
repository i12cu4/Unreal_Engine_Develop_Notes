import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs

# 生成一些示例数据
data, labels = make_blobs(n_samples=300, centers=3, cluster_std=0.60, random_state=0)

# 中心化数据
mean = np.mean(data, axis=0)
centered_data = data - mean

# 计算协方差矩阵
cov_matrix = np.cov(centered_data, rowvar=False)

# 计算特征值和特征向量
eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

# 选择最大的两个特征向量对应的特征值
indices = np.argsort(eigenvalues)[::-1]
top_indices = indices[:2]
top_eigenvectors = eigenvectors[:, top_indices]

# 投影数据到新的特征空间
principal_components = np.dot(centered_data, top_eigenvectors)

# 绘制结果
plt.scatter(principal_components[:, 0], principal_components[:, 1], c=labels, cmap='viridis', edgecolor='k')
plt.title('Principal Component Analysis (PCA)')
plt.show()
