from math import inf
from copy import deepcopy
input_file_name = 'input.txt'
output_file_name = 'output.txt'
eps = 10e-5

def reading():
    with open(input_file_name, 'r') as r:
        matrix = []
        for line in r:
            s = line.split()
            matrix.append([int(i) for i in s])
    return matrix


def find_first_strategy(matrix):
    """ Находит наилучшую стратегию для игрока А при первой итерации """
    index = inf
    maximum = -inf
    for i in range(len(matrix)):
        m = max(matrix[i])
        if maximum < m:
            index = i
            maximum = m
    return index


def find_solution(matrix):
    """ Находит решение матричной игры m*n методом итераций
    k - количество итераций
    v_max[j] - максимально возможный накопленный проигрыш игрока B для j-ой стратегии
    v_min[i] - минимально возможный накопленный выигрыш игрока А для i-ой стратегии
    v = (v_max / k + v_min / k) / 2 - приблеженное значение цены игры
    p - считает стратегии игрока А
    q - считает стратегии игрока B
    """
    k = 1
    p = [0 for _ in range(len(matrix))]
    q = [0 for _ in range(len(matrix[0]))]

    index = find_first_strategy(matrix)
    v_min = deepcopy(matrix[index])
    p[index] += 1
    v_ = min(v_min) / k

    jindex = v_min.index(min(v_min))
    v_max = [matrix[i][jindex] for i in range(len(matrix))]
    q[jindex] += 1
    V = max(v_max) / k

    v = (V + v_) / 2

    while (V - v) > eps or (v_ - v) > eps:
        k += 1

        index = v_max.index(max(v_max))
        v_min = list(map(lambda x, y: x + y, v_min, matrix[index]))
        p[index] += 1
        v_ = min(v_min) / k

        jindex = v_min.index(min(v_min))
        for i in range(len(matrix[0])):
            v_max[i] += matrix[i][jindex]
        q[jindex] += 1
        V = max(v_max) / k

        v = (V + v_) / 2

    with open(output_file_name, 'w') as w:
        w.write('v = ' + str(v) + '\n')
        w.write('p1 = ' + str(p[0] / k) + '\n')
        w.write('p2 = ' + str(p[1] / k) + '\n')
        w.write('p3 = ' + str(p[2] / k) + '\n')
        w.write('q1 = ' + str(q[0] / k) + '\n')
        w.write('q2 = ' + str(q[1] / k) + '\n')
        w.write('q3 = ' + str(q[2] / k) + '\n')

if __name__ == '__main__':
    find_solution(reading())
