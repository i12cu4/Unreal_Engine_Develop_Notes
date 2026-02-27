#梯度提升
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score

# 加载数据
digits = load_digits()

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(digits.data, digits.target, test_size=0.2, random_state=42)

# 创建一个梯度提升分类器
gbc = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)

# 训练模型
gbc.fit(X_train, y_train)

# 预测
y_pred = gbc.predict(X_test)

# 计算准确率
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy:.2f}')

# 绘制准确率曲线
accuracy_list = []
n_estimators = range(1, gbc.n_estimators_ + 1)
for i in n_estimators:
    gbc.set_params(n_estimators=i)
    gbc.fit(X_train, y_train)
    y_pred = gbc.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    accuracy_list.append(accuracy)

plt.figure(figsize=(10, 6))
plt.plot(n_estimators, accuracy_list, marker='o')
plt.xlabel('Number of estimators')
plt.ylabel('Accuracy')
plt.title('Accuracy vs. Number of estimators')
plt.show()
