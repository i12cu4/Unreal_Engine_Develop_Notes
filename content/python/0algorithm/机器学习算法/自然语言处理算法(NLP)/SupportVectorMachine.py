#支持向量机
import numpy as np
import matplotlib.pyplot as plt

# 生成随机数据集
np.random.seed(42)
mean_class1 = [-2, -2]
cov_class1 = [[2, 1.5], [1.5, 2]]
mean_class2 = [3, 3]
cov_class2 = [[1, -0.5], [-0.5, 1]]

class1_data = np.random.multivariate_normal(mean_class1, cov_class1, 100)
class2_data = np.random.multivariate_normal(mean_class2, cov_class2, 100)

X = np.vstack((class1_data, class2_data))
y = np.hstack((np.zeros(100), np.ones(100)))

# 绘制数据点
plt.scatter(class1_data[:, 0], class1_data[:, 1], label='Class 1')
plt.scatter(class2_data[:, 0], class2_data[:, 1], label='Class 2')

from sklearn.svm import SVC

# 定义并拟合SVM模型
svm = SVC(kernel='linear', C=1.0)
svm.fit(X, y)

# 绘制决策边界
ax = plt.gca()
xlim = ax.get_xlim()
ylim = ax.get_ylim()

xx = np.linspace(xlim[0], xlim[1], 30)
yy = np.linspace(ylim[0], ylim[1], 30)
YY, XX = np.meshgrid(yy, xx)
xy = np.vstack([XX.ravel(), YY.ravel()]).T
Z = svm.decision_function(xy).reshape(XX.shape)

ax.contour(XX, YY, Z, colors='k', levels=[-1, 0, 1], alpha=0.5, linestyles=['--', '-', '--'])

# 绘制支持向量
ax.scatter(svm.support_vectors_[:, 0], svm.support_vectors_[:, 1], s=100, linewidth=1, facecolors='none', edgecolors='k', label='Support Vectors')

plt.xlabel('X1')
plt.ylabel('X2')
plt.title('Support Vector Machine')
plt.legend()
plt.show()
