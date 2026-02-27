#朴素贝叶斯
import numpy as np
import matplotlib.pyplot as plt

# 1. 生成训练数据
def generate_data():
    # 生成两类数据
    class_1 = np.random.normal(loc=2, scale=1, size=(100, 2))
    class_2 = np.random.normal(loc=6, scale=1, size=(100, 2))

    # 添加噪声点
    class_1[np.random.choice(class_1.shape[0], 10, replace=False)] = np.random.normal(loc=4, scale=1, size=(10, 2))
    class_2[np.random.choice(class_2.shape[0], 10, replace=False)] = np.random.normal(loc=5, scale=1, size=(10, 2))

    X = np.vstack([class_1, class_2])
    y = np.array([0] * class_1.shape[0] + [1] * class_2.shape[0])

    return X, y

# 2. 计算概率
def calculate_probabilities(X, y):
    n_samples, n_features = X.shape
    classes = np.unique(y)
    n_classes = len(classes)

    # 初始化概率
    priors = np.zeros(n_classes)
    posteriors = [np.zeros((n_classes, n_features)) for _ in range(n_features)]

    for idx, c in enumerate(classes):
        # 计算先验概率
        priors[idx] = np.sum(y == c) / n_samples

        # 计算条件概率
        for f_idx in range(n_features):
            posteriors[f_idx][idx, :] = np.sum(X[y == c, f_idx] / np.sum(X[y == c, f_idx]))

    return priors, posteriors

# 3. 进行分类
def classify(X, y, test_data):
    priors, posteriors = calculate_probabilities(X, y)

    # 对测试数据进行分类
    predictions = np.log(priors) + np.dot(test_data, np.log(posteriors).T)
    return np.argmax(predictions, axis=1)

# 4. 可视化结果
def visualize(X, y):
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis')
    plt.xlabel('Feature 1')
    plt.ylabel('Feature 2')
    plt.title('Scatter plot of the data')
    plt.show()

if __name__ == "__main__":
    X, y = generate_data()
    visualize(X, y)

    test_data = np.random.normal(loc=4, scale=1, size=(10, 2))
    predictions = classify(X, y, test_data)
    print(f"Predictions for test data: {predictions}")
