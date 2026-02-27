#神经网络
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

# 设置随机数种子以确保结果的可重复性
tf.random.set_seed(0)

# 定义输入和输出数据
inputs = np.array([[0, 0],
                   [0, 1],
                   [1, 0],
                   [1, 1]])

outputs = np.array([[0],
                    [1],
                    [1],
                    [0]])

# 将输入和输出数据转换为 TensorFlow 张量
inputs_tensor = tf.convert_to_tensor(inputs, dtype=tf.float32)
outputs_tensor = tf.convert_to_tensor(outputs, dtype=tf.float32)

# 定义神经网络模型
model = tf.keras.Sequential([
    tf.keras.layers.Dense(3, activation='sigmoid', input_shape=(2,)),
    tf.keras.layers.Dense(1, activation='sigmoid')
])


# 编译模型
model.compile(optimizer='adam',
              loss='mean_squared_error')

# 训练神经网络
model.fit(inputs_tensor, outputs_tensor, epochs=2000, verbose=0)

# 使用模型进行预测
predictions = model.predict(inputs_tensor)

# 绘制图形
plt.figure(figsize=(10, 6))
plt.scatter(inputs[:, 0], outputs, c='blue', label='Actual')
plt.scatter(inputs[:, 0], predictions, c='red', label='Predicted')
plt.xlabel('Input 1')
plt.ylabel('Output')
plt.title('Neural Network Predictions')
plt.legend()
plt.show()
