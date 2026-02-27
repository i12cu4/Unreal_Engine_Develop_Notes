#粒子群优化
import numpy as np
import matplotlib.pyplot as plt

# 定义目标函数
def fitness_function(x):
    return x**2 + 3*x + 4

# 定义粒子群优化算法
def particle_swarm_optimization(num_particles, iterations):
    # 初始化粒子群的位置和速度
    positions = np.random.uniform(low=-10, high=10, size=num_particles)
    velocities = np.random.uniform(low=-1, high=1, size=num_particles)

    # 初始化个体最优位置和适应度
    personal_best_positions = positions.copy()
    personal_best_fitness = [fitness_function(pos) for pos in positions]

    # 全局最优位置和适应度
    global_best_position = positions[np.argmin(personal_best_fitness)]
    global_best_fitness = np.min(personal_best_fitness)

    # 记录全局最优位置变化过程
    history = [global_best_fitness]

    # 粒子群优化迭代
    for _ in range(iterations):
        # 更新粒子的速度和位置
        inertia_weight = 0.7
        cognitive_weight = 1.5
        social_weight = 1.5

        for i in range(num_particles):
            # 更新速度
            velocities[i] = (inertia_weight * velocities[i] +
                             cognitive_weight * np.random.random() * (personal_best_positions[i] - positions[i]) +
                             social_weight * np.random.random() * (global_best_position - positions[i]))

            # 更新位置
            positions[i] += velocities[i]

            # 更新个体最优位置和适应度
            fitness = fitness_function(positions[i])
            if fitness < personal_best_fitness[i]:
                personal_best_fitness[i] = fitness
                personal_best_positions[i] = positions[i]

                # 更新全局最优位置和适应度
                if fitness < global_best_fitness:
                    global_best_fitness = fitness
                    global_best_position = positions[i]

        history.append(global_best_fitness)

    return history

# 运行粒子群优化算法
num_particles = 30
iterations = 50
best_fitness_history = particle_swarm_optimization(num_particles, iterations)

# 绘制全局最优适应度的变化过程
plt.plot(best_fitness_history)
plt.xlabel('Iterations')
plt.ylabel('Global Best Fitness (minimized value)')
plt.title('Particle Swarm Optimization')
plt.show()
