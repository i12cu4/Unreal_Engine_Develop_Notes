#K均值聚类
import numpy as np
import matplotlib.pyplot as plt

def kmeans_custom(X, n_clusters, max_iters=100, tol=1e-4):
    # 随机初始化簇中心
    centers = X[np.random.choice(range(len(X)), n_clusters, replace=False)]
    
    for _ in range(max_iters):
        # 计算每个样本到簇中心的距离
        distances = np.linalg.norm(X[:, np.newaxis] - centers, axis=2)
        
        # 分配样本到最近的簇
        labels = np.argmin(distances, axis=1)
        
        # 更新簇中心
        new_centers = np.array([X[labels == i].mean(axis=0) for i in range(n_clusters)])
        
        # 检查收敛
        if np.linalg.norm(new_centers - centers) < tol:
            break
        
        centers = new_centers
    
    return centers, labels

# 生成一些示例数据
data, _ = make_blobs(n_samples=300, centers=3, cluster_std=0.60, random_state=0)

# 运行自定义K-Means
centers_custom, labels_custom = kmeans_custom(data, n_clusters=3)

# 绘制结果
plt.scatter(data[:, 0], data[:, 1], c=labels_custom, cmap='viridis', edgecolor='k')
plt.scatter(centers_custom[:, 0], centers_custom[:, 1], c='red', marker='X', s=200, alpha=0.75)
plt.title('Custom K-Means Clustering')
plt.show()
