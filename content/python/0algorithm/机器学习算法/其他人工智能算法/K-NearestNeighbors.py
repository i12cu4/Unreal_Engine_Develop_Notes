#K最近邻
import numpy as np
import matplotlib.pyplot as plt

# 生成随机数据集
np.random.seed(42)
class1_data = np.random.randn(50, 2)
class2_data = np.random.randn(50, 2) + np.array([2.5, 2.5])

X = np.vstack((class1_data, class2_data))
y = np.hstack((np.zeros(50), np.ones(50)))

# 定义KNN算法
def knn_predict(X_train, y_train, x_test, k=3):
    distances = np.sqrt(np.sum((X_train - x_test) ** 2, axis=1))  # 计算欧式距离
    nearest_indices = np.argsort(distances)[:k]  # 找到最近的k个样本的索引
    nearest_labels = y_train[nearest_indices].astype(int)  # 转换为整数类型
    return np.bincount(nearest_labels).argmax()  # 返回出现次数最多的标签作为预测结果

# 对数据进行预测并绘制结果
h = 0.1  # 网格步长
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

predictions = []
for i in range(xx.ravel().shape[0]):
    point = np.array([xx.ravel()[i], yy.ravel()[i]])
    pred = knn_predict(X, y, point, k=5)
    predictions.append(pred)

predictions = np.array(predictions).reshape(xx.shape)

plt.contourf(xx, yy, predictions, cmap=plt.cm.Paired, alpha=0.8)
plt.scatter(class1_data[:, 0], class1_data[:, 1], label='Class 0')
plt.scatter(class2_data[:, 0], class2_data[:, 1], label='Class 1')
plt.xlabel('X1')
plt.ylabel('X2')
plt.title('K Nearest Neighbors')
plt.legend()
plt.show()
