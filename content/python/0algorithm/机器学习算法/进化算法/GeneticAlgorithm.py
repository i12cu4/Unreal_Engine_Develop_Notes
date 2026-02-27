#遗传算法
import numpy as np
import matplotlib.pyplot as plt

# 定义适应度函数（目标函数）
def fitness_function(x):
    return x**2 + 3*x + 4

# 遗传算法
def genetic_algorithm(population_size, generations):
    population = np.random.uniform(low=-10, high=10, size=population_size)
    history = []

    for generation in range(generations):
        fitness_scores = [fitness_function(individual) for individual in population]

        # 选择（选择较优秀的个体）
        sorted_indices = np.argsort(fitness_scores)
        sorted_population = population[sorted_indices]

        # 交叉（从较优秀的个体中随机选择进行交叉）
        crossover_point = population_size // 2
        children = []
        for i in range(crossover_point, population_size, 2):
            parent1 = sorted_population[np.random.randint(0, crossover_point)]
            parent2 = sorted_population[np.random.randint(0, crossover_point)]
            child1 = np.mean([parent1, parent2])
            child2 = np.mean([parent1, parent2])
            children.extend([child1, child2])

        # 突变（对新一代个体进行随机突变）
        mutation_rate = 0.1
        num_mutations = int(mutation_rate * population_size)
        mutation_indices = np.random.choice(population_size, num_mutations, replace=False)
        population[mutation_indices] += np.random.uniform(-1, 1, num_mutations)

        population[:population_size - crossover_point] = children
        history.append(sorted_population[0])  # 记录每一代的最优解

    return history

# 运行遗传算法
generations = 50
population_size = 100
best_individuals = genetic_algorithm(population_size, generations)

# 绘制每一代最优解的变化过程
plt.plot(best_individuals)
plt.xlabel('Generations')
plt.ylabel('Best Individual (minimized value)')
plt.title('Genetic Algorithm')
plt.show()
