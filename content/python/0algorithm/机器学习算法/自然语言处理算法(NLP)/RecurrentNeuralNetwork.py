#循环神经网络
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense

# 生成随机序列数据集
np.random.seed(42)
seq_length = 20
num_samples = 200

# 创建随机序列数据
sequences = np.random.rand(num_samples, seq_length, 1)
target = np.sum(sequences, axis=1)

# 构建RNN模型
model = Sequential([
    SimpleRNN(10, input_shape=(seq_length, 1), activation='relu'),
    Dense(1)
])

# 编译模型
model.compile(optimizer='adam', loss='mse')

# 训练模型
history = model.fit(sequences, target, epochs=10, batch_size=32, validation_split=0.2)

# 绘制训练过程中的损失变化
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.legend()
plt.show()
