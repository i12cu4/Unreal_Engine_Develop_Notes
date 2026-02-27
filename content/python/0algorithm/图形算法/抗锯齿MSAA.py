import pygame
import sys

# 初始化Pygame
pygame.init()

# 设置屏幕宽度和高度
WIDTH, HEIGHT = 800, 600

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# 设置MSAA级别
msaa_level = 4  # 你可以根据需要调整级别

# 创建一个渲染目标，用于MSAA
msaa_target = pygame.Surface((WIDTH * msaa_level, HEIGHT * msaa_level), pygame.SRCALPHA)

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 渲染场景到MSAA目标
    msaa_target.fill((0, 0, 0, 0))  # 清空MSAA目标

    # 在MSAA目标上绘制矩形
    pygame.draw.rect(msaa_target, (255, 0, 0), (100 * msaa_level, 100 * msaa_level, 200 * msaa_level, 200 * msaa_level))

    # 在MSAA目标上绘制圆形
    pygame.draw.circle(msaa_target, (0, 0, 255), (400 * msaa_level, 300 * msaa_level), 100 * msaa_level)

    # 缩小MSAA目标以进行抗锯齿处理
    scene = pygame.transform.smoothscale(msaa_target, (WIDTH, HEIGHT))

    # 在屏幕上绘制抗锯齿处理后的场景
    screen.blit(scene, (0, 0))

    pygame.display.flip()

# 游戏循环结束后，退出Pygame
pygame.quit()
sys.exit()
