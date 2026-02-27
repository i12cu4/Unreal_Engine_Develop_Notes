#长短期记忆网络
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# 生成一些示例数据
def generate_data():
    t = np.arange(0, 10, 0.1)
    sin_wave = np.sin(t)
    return sin_wave

# 创建LSTM模型
def create_lstm_model():
    model = Sequential()
    model.add(LSTM(units=50, activation='relu', input_shape=(1, 1)))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mse')
    return model

# 准备数据
data = generate_data()
data = data.reshape((len(data), 1, 1))

# 创建和训练模型
model = create_lstm_model()
model.fit(data, data, epochs=100, verbose=0)

# 用模型进行预测
predictions = model.predict(data)

# 绘制结果
plt.plot(data[:, 0, 0], label='Original Data')
plt.plot(predictions[:, 0], label='Predictions')
plt.legend()
plt.show()
