#自编码器
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs

# 生成一些示例数据
data, _ = make_blobs(n_samples=300, centers=3, cluster_std=0.60, random_state=0)

# 定义Autoencoder的架构
input_size = data.shape[1]
hidden_size = 2  # 将数据降维到2维
output_size = input_size

# 初始化权重和偏置
weights_encoder = np.random.randn(input_size, hidden_size)
bias_encoder = np.zeros(hidden_size)
weights_decoder = np.random.randn(hidden_size, output_size)
bias_decoder = np.zeros(output_size)

# 定义激活函数（使用sigmoid）
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# 定义Autoencoder的训练过程
def train_autoencoder(data, weights_encoder, bias_encoder, weights_decoder, bias_decoder, epochs=1000, learning_rate=0.01):
    for epoch in range(epochs):
        # 前向传播
        encoded = sigmoid(np.dot(data, weights_encoder) + bias_encoder)
        decoded = sigmoid(np.dot(encoded, weights_decoder) + bias_decoder)

        # 计算损失（均方误差）
        loss = np.mean((decoded - data)**2)

        # 反向传播
        error = decoded - data
        gradient_decoder = np.dot(encoded.T, error)
        gradient_encoder = np.dot(error, weights_decoder.T) * encoded * (1 - encoded)

        # 更新权重和偏置
        weights_decoder -= learning_rate * gradient_decoder
        bias_decoder -= learning_rate * np.mean(error, axis=0)
        weights_encoder -= learning_rate * np.dot(data.T, gradient_encoder)
        bias_encoder -= learning_rate * np.mean(gradient_encoder, axis=0)

        # 打印损失
        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Loss: {loss}")

    return weights_encoder, bias_encoder, weights_decoder, bias_decoder

# 训练Autoencoder
trained_weights_encoder, trained_bias_encoder, trained_weights_decoder, trained_bias_decoder = train_autoencoder(
    data, weights_encoder, bias_encoder, weights_decoder, bias_decoder
)

# 使用训练后的Autoencoder进行降维
encoded_data = sigmoid(np.dot(data, trained_weights_encoder) + trained_bias_encoder)

# 绘制结果
plt.scatter(encoded_data[:, 0], encoded_data[:, 1], c=_, cmap='viridis', edgecolor='k')
plt.title('Autoencoder')
plt.show()
