#逻辑回归
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

# 创建模拟数据
X, y = make_classification(n_samples=100, n_features=20, n_redundant=2, n_classes=2, random_state=42)

# 创建Logistic回归模型
model = LogisticRegression(solver='lbfgs', multi_class='ovr')
model.fit(X, y)

# 预测数据
y_pred = model.predict(X)

# 绘制图形
plt.figure(figsize=(10, 6))
plt.scatter(X[:, 0], X[:, 1], c=y, edgecolors='k', marker='o', label='True')
plt.scatter(X[:, 0], X[:, 1], c=y_pred, edgecolors='k', marker='s', label='Predicted')
plt.title('Logistic Regression')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.legend()
plt.show()
