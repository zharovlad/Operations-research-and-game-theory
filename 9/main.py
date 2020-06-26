from math import inf
from copy import deepcopy
input_file_name = 'input2.txt'
output_file_name = 'output.txt'
eps = 10e-2

def get_starting_data():
    """ Получаем данные из входного файла
    Первая строка (вектор а) - количество произведенного товара
    Вторая строка (вектор b) - количество необходимого товара
    Затем таблица издержек (матрица c)
    Пример содержания входного файла:
    30 40 20
    20 30 30 10

    2 3 2 4
    3 2 5 1
    4 3 2 6
    """
    with open(input_file_name, 'r') as r:
        s = r.readline()
        s = s.split()
        a = [int(s[i]) for i in range(len(s))]
        s = r.readline()
        s = s.split()
        b = [int(s[i]) for i in range(len(s))]
        s = r.readline()
        c = []
        for i in range(len(a)):
            s = r.readline()
            s = s.split()
            array = []
            for j in range(len(s)):
                array.append(int(s[j]))
            c.append(array)

    return [a, b, c]


def sum(a):
    """ Возвращает сумму всех элементов вектора """
    s = 0
    for i in a:
        if i < 0:
            with open(output_file_name, 'w') as w:
                w.write('Ошибка ввода. Один из элементов вектора отрицателен')
            exit(1)
        s += i
    return s


def north_west_method(data):
    """ Находит допустимый опорный план методом северо-западного угла
    Выводит исходные данные """
    a = data[0]
    b = data[1]
    c = data[2]
    with open(output_file_name, 'w') as w:
        w.write('a = ' + str(a) + '\n')
        w.write('b = ' + str(b) + '\n')
        w.write('\nИсходная матрица\n')
        for i in c:
            for j in i:
                w.write(str(j).center(5))
            w.write('\n')
        result = [[0 for _ in range(len(b))] for __ in range(len(a))]

        # если задача несбалансированная,
        # вводим дополнительного фиктивного поставщика или потребителя (столбец или строку)

        if sum(a) < sum(b):
            result.append([0 for _ in range(len(result[0]))])
            data[2].append([0 for _ in range(len(result[0]))])
            a.append(sum(b) - sum(a))
        elif sum(a) > sum(b):
            for i in range(len(result)):
                result[i].append(0)
                data[2][i].append(0)
            b.append(sum(a) - sum(b))
        i = 0
        j = 0
        _a = deepcopy(a)
        _b = deepcopy(b)

        # составляем первичный опорный план
        while sum(_a) != 0 and sum(_b) != 0:
            temp = min(_a[i], _b[j])
            result[i][j] = temp
            _b[j] -= temp
            _a[i] -= temp
            if _a[i] == 0:
                i += 1
            else:
                j += 1

    return result


def print_oporniy(result, c, a, b):
    """ Печать опорного плана в файл """
    with open(output_file_name, 'a') as w:
        w.write('\nОпорный план\n')
        w.write(' ' * (6 * len(b) - 2) + 'a\n ')
        for i in range(len(result)):
            for j in range(len(result[0])):
                w.write(str(result[i][j]).center(5))
            w.write(str(a[i]).center(5) + '\n')
            if i != len(result) - 1:
                w.write(' ')
            else:
                w.write('b')
        for i in range(len(b)):
            w.write(str(b[i]).center(5))
        w.write('\n')
        count_F(result, c, w)
        w.write('_' * 50 + '\n')


def count_F(oporniy, table, w):
    """ Посчитать значение F = cij * xij и вывести в файл """
    F = 0
    for i in range(len(table)):
        for j in range(len(table[i])):
            F += oporniy[i][j] * int(table[i][j])
    w.write('F = ' + str(F) + '\n')


def potential(data):
    """ Находит оптимальное решение методом потенциалов """
    result = north_west_method(data)  # получим первый опорный план методом северо-западного угла
    a = data[0]
    b = data[1]
    c = data[2]
    # посчитаем значение F для опорного плана
    print_oporniy(result, c, a, b)
    while True:
        # найдем потенциалы
        pa, pb = count_potential_value(result, c)
        # найдём матрицу H
        H = create_H_matrix(c, pa, pb)
        # распечатаем её
        print_matrix_H(H, pa, pb)
        # найдём цикл начиная с минимального отрицательного элемента в H
        cycle = determine_cycle(H, result)
        # если все элементы в H положительные - выводим ответ
        if not cycle:
            with open(output_file_name, 'a') as w:
                w.write('Полученный опорный план - оптимальный\n')
                w.write('Все элементы матрицы H > 0\n')
            break
        # удалим из цикла дублирующуюся вершину
        cycle.pop()
        # оптимизируем опорный план
        result = get_new_result(cycle, result)
        print_oporniy(result, c, a, b)


def count_potential_value(result, c):
    """ Считает значения потенциалов pb и pa так, чтобы cij - (pbj - pai ) = 0"""
    pa = [inf for _ in range(len(data[0]))]
    pb = [inf for _ in range(len(data[1]))]
    pa[0] = 0  # pa[0] - для начала расчета
    f = True
    while f:
        is_not_change = True
        for i in range(len(c)):
            for j in range(len(c[i])):
                if result[i][j] != 0:
                    if pa[i] != inf and pb[j] == inf:
                        pb[j] = c[i][j] + pa[i]
                        is_not_change = False
                    elif pb[j] != inf and pa[i] == inf:
                        pa[i] = pb[j] - c[i][j]
                        is_not_change = False

        # если решение невырожденное, приравниваем одну из нулевых ячеек матрицы к eps
        # eps - (число незначительно отличающееся от 0)
        if is_not_change:
            for i in range(len(pa)):
                if pa[i] == inf:
                    for j in range(len(pb)):
                        if pb[j] != inf:
                            result[i][j] = eps
                            break
                    break

        f = False
        for i in pa:
            if i == inf:
                f = True
                break

        for j in pb:
            if j == inf:
                f = True
                break

    return pa, pb


def create_H_matrix(c, pa, pb):
    """ Создает промежуточную матрицу hij = cij - ( pbj - pai ) """
    return [[c[i][j] - (pb[j] - pa[i]) for j in range(len(pb))] for i in range(len(pa))]


def print_matrix_H(H, pa, pb):
    """ Печатает матрицу H с потенциалами """
    with open(output_file_name, 'a') as w:
        w.write('Матрица H (вспомогательная):\n')
        w.write(' ' * 6 * len(pb) + 'pa\n  ')
        for i in range(len(H)):
            for j in range(len(H[0])):
                w.write(str(H[i][j]).center(5))
            w.write(str(pa[i]).center(5) + '\n')
            if i != len(H) - 1:
                w.write('  ')
            else:
                w.write('pb')
        for i in range(len(pb)):
            w.write(str(pb[i]).center(5))
        w.write('\n')


def determine_cycle(H, result):
    """ Находим цикл """
    # сначала нужно найти минимальный отрицательный элемент
    index, jindex = find_min_in_H(H)
    if index == inf:
        return False
    # от минимума ищем цикл
    return find_next_vertice(index, jindex, H, result, [], 'string')


def find_min_in_H(H):
    """ Возвращает индексы мимнимального отрицательного элемента матрицы
    Если все элементы положительные - возвращает inf, inf """
    index = inf
    jindex = inf
    min = inf
    for i in range(len(H)):
        for j in range(len(H[i])):
            if H[i][j] < min:
                min = H[i][j]
                index = i
                jindex = j
    return index, jindex


def find_next_vertice(index, jindex, H, result, cycle, side):
    """ Находит индекс следующей вершины (рекурсивная функция) """
    if len(cycle) < 1:
        cycle.append([index, jindex])
        result[index][jindex] = inf
    else:
        if result[index][jindex] == inf:
            if len(cycle) % 2 == 0:
                cycle.append([index, jindex])
                result[index][jindex] = 0
            return cycle

        for i in cycle:
            if [index, jindex] == i:
                return cycle

        cycle.append([index, jindex])
    i = index
    j = jindex

    old = deepcopy(cycle)

    if side == 'string':
        for k in range(len(H[i])):
            if k == j:
                continue
            if result[i][k] != 0:
                cycle = find_next_vertice(i, k, H, result, cycle, 'column')
                if cycle != old:
                    return cycle

    if side == 'column':
        for k in range(len(H)):
            if k == i:
                continue
            if result[k][j] != 0:
                cycle = find_next_vertice(k, j, H, result, cycle, 'string')
                if cycle != old:
                    return cycle
    cycle.pop()
    return cycle


def find_min_in_cycle(cycle, result):
    """ Возвращает минимальный элемент (значение), стоящий на четном месте в маршруте (индексы cycle 1, 3, 5, ...)
    Нужен для изменения значений в result """
    min = inf
    for i in range(1, len(cycle), 2):
        if result[cycle[i][0]][cycle[i][1]] < min:
            min = result[cycle[i][0]][cycle[i][1]]
    return min


def get_new_result(cycle, result):
    """ Производится прибавление min ко всем четным элементам маршрута (0, 2, 4...)
    и вычитание min из всех не четных элементов маршрута (1, 3, 5...) """
    # определим минимальный элемент, стоящий на четном месте в маршруте (индексы cycle 1, 3, 5, ...)
    min = find_min_in_cycle(cycle, result)
    for i in range(len(cycle)):
        result[cycle[i][0]][cycle[i][1]] += min
        min *= -1
    return result


if __name__ == '__main__':
    data = get_starting_data()
    potential(data)
