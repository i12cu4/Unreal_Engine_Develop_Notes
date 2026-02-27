from PIL import Image
import numpy as np

# 打开图像文件
image = Image.open("texture.png")  # 替换为你的纹理图像文件

# 获取图像的原始宽度和高度
width, height = image.size

# 创建一个空的Mipmap层级列表
mipmap_levels = []

# 将原始纹理添加到最高级别（level 0）
mipmap_levels.append(np.array(image))

# 生成Mipmap层级
while width > 1 and height > 1:
    width //= 2
    height //= 2
    resized_image = image.resize((width, height), Image.ANTIALIAS)  # 使用抗锯齿缩小图像
    mipmap_levels.append(np.array(resized_image))

# 在这里，mipmap_levels 是一个包含所有Mipmap层级的列表，从高分辨率到低分辨率

# 示例：访问不同级别的Mipmap纹理
level = 0  # 选择要使用的Mipmap级别
if level < len(mipmap_levels):
    mip_texture = Image.fromarray(mipmap_levels[level])
    mip_texture.show()  # 显示所选级别的Mipmap纹理

# 保存不同级别的Mipmap纹理到文件
for level, mip_level in enumerate(mipmap_levels):
    mip_texture = Image.fromarray(mip_level)
    mip_texture.save(f"mipmap_level_{level}.png")  # 保存为文件
