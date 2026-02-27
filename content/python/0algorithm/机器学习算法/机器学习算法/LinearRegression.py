#线性回归
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 创建样本数据
# 让我们假设一个变量（X）与另一个变量（y）有线性关系
# X是独立变量，y是依赖变量
np.random.seed(0)  # 为了可重复性设置随机种子
X = np.random.rand(100, 1) * 10  # 生成100个随机数作为X
y = 2 * X + 1 + np.random.randn(100, 1) * 0.05  # y是X的线性函数加上一些噪声

# 划分数据集为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# 创建线性回归模型实例
model = LinearRegression()

# 训练模型
model.fit(X_train, y_train)

# 使用模型进行预测
y_pred = model.predict(X_test)

# 计算预测的准确性
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# 打印模型的参数
print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_}")

# 绘制数据点和回归线
plt.scatter(X_test, y_test, color='blue', label='Actual data')
plt.plot(X_test, y_pred, color='red', linewidth=2, label='Regression line')
plt.xlabel('X')
plt.ylabel('y')
plt.title('Linear Regression')
plt.legend()
plt.show()
