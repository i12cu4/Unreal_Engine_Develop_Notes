#卷积神经网络
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical
import tensorflow.compat.v1 as tf

tf.disable_v2_behavior()

# 生成随机图像数据集
np.random.seed(42)
num_samples = 200
image_size = 28

# 创建两个类别的随机图像数据
class1_images = np.random.rand(num_samples, image_size, image_size)
class2_images = np.random.rand(num_samples, image_size, image_size)

# 合并图像和对应的标签
X = np.concatenate((class1_images, class2_images), axis=0)
y = np.hstack((np.zeros(num_samples), np.ones(num_samples)))

# 将图像数据reshape成适当的格式（增加通道维度）
X = X.reshape(-1, image_size, image_size, 1)

# 将标签进行独热编码
y = to_categorical(y)

# 构建CNN模型
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(image_size, image_size, 1)),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(2, activation='softmax')
])

# 编译模型
model.compile(optimizer=tf.compat.v1.train.AdamOptimizer(), loss='categorical_crossentropy', metrics=['accuracy'])

# 训练模型
history = model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2)

# 绘制训练过程中的准确度和损失变化
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['acc'], label='Training Accuracy')
plt.plot(history.history['val_acc'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.legend()

plt.tight_layout()
plt.show()
