#逻辑回归
import numpy as np
import matplotlib.pyplot as plt

# 生成随机数据集
np.random.seed(42)
# 创建两个类别的随机数据点
mean_class1 = [-2, -2]
cov_class1 = [[2, 1.5], [1.5, 2]]
mean_class2 = [3, 3]
cov_class2 = [[1, -0.5], [-0.5, 1]]

class1_data = np.random.multivariate_normal(mean_class1, cov_class1, 100)
class2_data = np.random.multivariate_normal(mean_class2, cov_class2, 100)

# 合并数据点和对应的标签
X = np.vstack((class1_data, class2_data))
y = np.hstack((np.zeros(100), np.ones(100)))

# 在数据中添加偏置列
X_with_bias = np.c_[np.ones(X.shape[0]), X]

# 定义逻辑回归模型
class LogisticRegression:
    def __init__(self, lr=0.01, num_iter=100000, fit_intercept=True):
        self.lr = lr
        self.num_iter = num_iter
        self.fit_intercept = fit_intercept

    def __sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def __add_intercept(self, X):
        intercept = np.ones((X.shape[0], 1))
        return np.concatenate((intercept, X), axis=1)

    def fit(self, X, y):
        if self.fit_intercept:
            X = self.__add_intercept(X)
        
        # 初始化权重
        self.theta = np.zeros(X.shape[1])

        for _ in range(self.num_iter):
            z = np.dot(X, self.theta)
            h = self.__sigmoid(z)
            gradient = np.dot(X.T, (h - y)) / y.size
            self.theta -= self.lr * gradient

    def predict_prob(self, X):
        if self.fit_intercept:
            X = self.__add_intercept(X)
        
        return self.__sigmoid(np.dot(X, self.theta))

    def predict(self, X, threshold=0.5):
        return self.predict_prob(X) >= threshold

# 实例化并训练模型
model = LogisticRegression(lr=0.1, num_iter=300000)
model.fit(X, y)

# 绘制数据点
plt.scatter(class1_data[:, 0], class1_data[:, 1], label='Class 1')
plt.scatter(class2_data[:, 0], class2_data[:, 1], label='Class 2')

# 绘制决策边界
x_values = [np.min(X[:, 0]), np.max(X[:, 0])]
y_values = - (model.theta[0] + np.dot(model.theta[1], x_values)) / model.theta[2]
plt.plot(x_values, y_values, label='Decision Boundary', c='red')

plt.xlabel('X1')
plt.ylabel('X2')
plt.title('Logistic Regression')
plt.legend()
plt.show()
