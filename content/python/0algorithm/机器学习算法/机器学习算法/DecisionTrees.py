#决策树
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

# 1. 加载鸢尾花数据集
iris = load_iris()
X = iris.data
y = iris.target

# 2. 使用决策树分类器训练模型
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
clf = DecisionTreeClassifier(random_state=42)
clf.fit(X_train, y_train)

# 3. 绘制决策树
plt.figure(figsize=(12, 8))
plot_tree(clf, feature_names=iris.feature_names, class_names=list(iris.target_names), filled=True)
plt.show()
