#支持向量机
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix

# 创建数据集
X, y = make_blobs(n_samples=300, centers=2, random_state=42, cluster_std=1.05)

# 为了可视化，我们只使用前两个特征
plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('Data Visualization')
plt.show()

# 将数据集分为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建 SVM 模型
svm_model = SVC(kernel='linear', C=1, random_state=42)

# 训练模型
svm_model.fit(X_train, y_train)

# 使用训练好的模型进行预测
y_pred = svm_model.predict(X_test)

# 评估模型性能
print("Classification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 绘制决策边界
def plot_decision_boundary(model, X, y, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 8))
    
    # 绘制数据
    ax.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis', edgecolors='k', s=50)

    # 计算决策边界
    x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx1, xx2 = np.meshgrid(np.linspace(x1_min, x1_max, 100),
                           np.linspace(x2_min, x2_max, 100))
    Z = model.decision_function(np.c_[xx1.ravel(), xx2.ravel()])
    Z = Z.reshape(xx1.shape)
    ax.contourf(xx1, xx2, Z, alpha=0.8, cmap='viridis')
    ax.set_title('Decision Boundary')
    ax.set_xlabel('Feature 1')
    ax.set_ylabel('Feature 2')

# 绘制决策边界
plot_decision_boundary(svm_model, X, y)
plt.show()
