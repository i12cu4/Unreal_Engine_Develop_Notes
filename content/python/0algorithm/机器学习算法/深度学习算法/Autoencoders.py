import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# 生成一些示例数据
def generate_data():
    t = np.arange(0, 10, 0.1)
    sin_wave = np.sin(t)
    return sin_wave

# 创建Autoencoder模型
def create_autoencoder_model():
    model = Sequential()
    model.add(Dense(units=8, activation='relu', input_shape=(1,)))
    model.add(Dense(units=1, activation='linear'))
    model.compile(optimizer='adam', loss='mse')
    return model

# 准备数据
data = generate_data()

# 添加噪声
noisy_data = data + np.random.normal(0, 0.2, size=len(data))

# 创建并训练Autoencoder模型
model = create_autoencoder_model()
model.fit(noisy_data, data, epochs=100, verbose=0)

# 使用Autoencoder模型进行重构
reconstructed_data = model.predict(noisy_data)

# 绘制结果
plt.plot(data, label='Original Data')
plt.plot(noisy_data, label='Noisy Data')
plt.plot(reconstructed_data, label='Reconstructed Data')
plt.legend()
plt.show()
