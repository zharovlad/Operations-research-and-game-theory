from math import inf
from copy import deepcopy
input_file_name = 'input3.txt'
output_file_name = 'output.txt'


def print_starting_data():
    """ Печатает входные данные: F и ограничения """
    writing = open(output_file_name, 'w')
    reading = open(input_file_name, 'r')
    m = reading.readline().split()[0]
    s = reading.readline().split()
    writing.write('F = ')
    for i in range(len(s)):
        writing.write(s[i] + 'x' + str(i + 1) + '  +  ')
    writing.write('-> ' + m)
    writing.write('\n\nОграничения:\n')
    for line in reading:
        s = line.split()
        for i in range(len(s) - 2):
            writing.write(str(s[i]) + ' x' + str(i + 1))
            writing.write('  +  ')

        writing.write(' ' + s[-2] + ' ')
        writing.write(str(float(s[-1])) + '\n')
    writing.close()
    reading.close()


def reading_from_file():
    """ Возвращает систему ограничений, F,
    Если задача на минимум - возвращает двойственную систему """
    dvoj = False
    reading = open(input_file_name, 'r')
    m = reading.readline().split()[0]
    s = reading.readline().split()
    f = [0.0]
    for each in s:
        f.append(-float(each))
    matrix = [f]
    for line in reading:
        s = line.split()
        array = []
        for i in range(len(s) - 2):
            array.append(float(s[i]))
        array.append(s[-2])
        array.append(float(s[-1]))
        matrix.append(array)
    reading.close()
    if m == 'min' and matrix[1][-2] != '=':
        dvoj = True
        f = [-matrix[i][-1] for i in range(1, len(matrix), 1)]
        f.insert(0, 0.0)
        result = [[matrix[j][i] for j in range(1, len(matrix), 1)] for i in range(len(matrix[1]) - 2)]
        symbol = '>=' if result[1][-2] == '<=' else '<='

        for i in range(len(result)):
            result[i].append(symbol)
            result[i].append(-matrix[0][i + 1])
        result.insert(0, f)
        matrix = result
        writing = open(output_file_name, 'a')
        writing.write('\nРешаем двойственную задачу\n')
        writing.write('F = ')
        for i in range(1, len(matrix[0]), 1):
            writing.write(str(-matrix[0][i]) + ' x' + str(i) + '  +  ')
        writing.write('-> max')
        writing.write('\n\nОграничения:\n')
        for i in range(1, len(matrix), 1):
            for j in range(len(matrix[i]) - 2):
                writing.write(str(matrix[i][j]) + ' x' + str(j + 1))
                writing.write('  +  ')

            writing.write(' ' + str(matrix[i][-2]) + ' ')
            writing.write(str(float(matrix[i][-1])) + '\n')
        writing.close()

    return matrix, dvoj


def to_canonical(matrix):
    """ Приводит систему уравнений к каноническому виду """

    # сначала переносим b в начало таблицы (для удобства)
    for i in range(1, len(matrix), 1):
        temp = matrix[i].pop()
        matrix[i].insert(0, temp)
    # Преобразуем таблицу, чтобы все b > 0
    for i in range(1, len(matrix), 1):
        if matrix[i][0] < 0:
            for j in range(len(matrix[i]) - 1):
                matrix[i][j] = -matrix[i][j]
            if matrix[i][-1] == '<=':
                matrix[i][-1] = '>='
            elif matrix[i][-1] == '>=':
                matrix[i][-1] = '<='
            else:
                matrix[i][-1] = '='

    # Если у нас неравенство, то
    # Если <=, то добавляем новую переменную с коэфициентом 1
    # Если >=, то добавляем новую переменную с коэфициентом -1

    matrix[0].append('!!!delete!!!')
    for i in range(1, len(matrix), 1):
        if matrix[i][-1] == '<=':
            for j in range(len(matrix)):
                if j == i:
                    matrix[j].insert(-1, 1.0)
                else:
                    matrix[j].insert(-1, 0.0)
        elif matrix[i][-1] == '>=':
            for j in range(len(matrix)):
                if j == i:
                    matrix[j].insert(-1, -1.0)
                else:
                    matrix[j].insert(-1, 0.0)

    # Удалим знаки
    for i in matrix:
        i.pop()

    # Смотрим, какие переменные могут стать базисными
    base_variables = [inf for _ in range(1, len(matrix), 1)]
    free_variables = [i for i in range(1, len(matrix[0]), 1)]
    for i in range(1, len(matrix), 1):
        for j in range(1, len(matrix[0]), 1):
            if matrix[i][j] == 1.0:
                base = True
                for k in range(len(matrix)):
                    if matrix[k][j] != 0.0:
                        if k == i:
                            continue
                        base = False
                        break
                if base:
                    base_variables[i - 1] = j

    amount_of_variables = len(free_variables)  # хранит количество переменных
    # Удалим из таблицы лишние столбцы (свободные переменные, которые стали базисные)
    temp = deepcopy(base_variables)
    for j in range(len(temp)):
        if temp[j] != inf:
            for i in range(len(matrix)):
                matrix[i].pop(temp[j])

            # А также индексы этих столбцов из free_variables
            free_variables.pop(free_variables.index(base_variables[j]))
            temp = [temp[k] - 1 for k in range(len(temp))]

    # Добавим искусственные переменные
    artificial_variables = []
    indexes_of_artificial_variables = []

    for j in range(len(base_variables)):
        if base_variables[j] == inf:
            amount_of_variables += 1
            base_variables[j] = amount_of_variables
            artificial_variables.append(amount_of_variables)
            indexes_of_artificial_variables.append(j + 1)

    return matrix, base_variables, free_variables, artificial_variables, indexes_of_artificial_variables


def print_simplex_table(T, matrix, indexes_of_variables, free_variables):
    """ Печатает симплекс таблицу """
    writing = open(output_file_name, 'a')
    writing.write('\n        b')
    for i in free_variables:
        writing.write('       x' + str(i) + ' ')
    writing.write('\n')

    writing.write('T  ')
    for j in range(len(T)):
        if T[j] < 0:
            writing.write(('-M').center(10))
        elif T[j] > 0:
            writing.write(('M').center(10))
        else:
            writing.write(('0').center(10))
    writing.write('\n')

    writing.write('F  ')
    for j in range(len(matrix[0])):
        writing.write(('%.5f' % matrix[0][j]).center(10))
    writing.write('\n')

    for i in range(1, len(matrix), 1):
         writing.write('x' + str(indexes_of_variables[i - 1]))
         for j in range(len(matrix[0])):
             writing.write((' %.5f' % matrix[i][j]).center(10))
         writing.write('\n')
    writing.write('\n')
    writing.close()


def search_solution(matrix, base_variables, free_variables, artificial_variables, indexes_of_artificial_variables, dvoj):
    """ Ищем решение """
    # построим линейную форму T(x)
    T = recount_T(matrix, indexes_of_artificial_variables)

    # печатаем симплекс таблицу на 0-ой итерации
    print_simplex_table(T, matrix, base_variables, free_variables)

    while True:
        # ищем разрешающий элемент
        # column - индекс разрешающего столбца
        # string - индекс разрешающей строки
        column = inf
        min = inf
        string = inf
        if max(T) == 0:
            for i, x in enumerate(matrix[0]):
                if x < min and x < 0:
                    min = x
                    column = i
            if min == inf:
                if dvoj:
                    dvoj_answer(matrix, base_variables, free_variables)
                else:
                    print_answer(matrix, base_variables)
                return 'Оптимальное решение получено'

            # ищем разрешающую строку
            # string - индекс разрешающей строки

            min = inf
            for i, s in enumerate(matrix):
                try:
                    if s[-1] / s[column] < min and s[column] > 0:
                        min = s[-1] / s[column]
                        string = i
                except:
                    continue
            if min == inf:
                return 'Оптимальное решение найти невозможно, так как F не ограничена на ОДР'
        else:
            for i, t in enumerate(T):
                if i == 0:
                    continue
                if t < min:
                    min = t
                    column = i
            min = inf

            for i in range(1, len(matrix), 1):
                try:
                    if matrix[i][0] / matrix[i][column] < min and matrix[i][column] > 0:
                        min = matrix[i][0] / matrix[i][column]
                        string = i
                except:
                    continue

            if string == inf:
                break

        old_f = matrix[0][0]

        # изменим индексы переменных

        base_variables[string - 1], free_variables[column - 1] = free_variables[column - 1], base_variables[string - 1]

        # составляем новую симплексную таблицу

        # сохраним старую симплекс-таблицу
        old = deepcopy(matrix)

        # новый разрешающий элемент
        matrix[string][column] = 1 / matrix[string][column]

        # новая разрешающая строка
        for i in range(len(matrix[0])):
            if i != column:
                matrix[string][i] = old[string][i] / old[string][column]

        # новый разрешающий столбец
        for i in range(len(matrix)):
            if i != string:
                matrix[i][column] = -matrix[i][column] / old[string][column]

        # остальные элементы новой симплекс таблицы
        for i in range(len(matrix)):
            if i == string:
                continue
            for j in range(len(matrix[0])):
                if j == column:
                    continue
                matrix[i][j] = old[i][j] + old[string][j] * matrix[i][column]

        # проверим, является ли новая свободная переменная искусственной

        for i in range(len(artificial_variables)):
            if artificial_variables[i] == free_variables[column - 1]:
                indexes_of_artificial_variables.pop(i)
                for each in matrix:
                    each.pop(column)
                free_variables.pop(free_variables.index(artificial_variables.pop(i)))
                break

        # пересчитаем линейную форму T(x)
        T = recount_T(matrix, indexes_of_artificial_variables)

        # печатаем симплекс таблицу после каждой итерации
        print_simplex_table(T, matrix, base_variables, free_variables)

        # сравним старое значение с новым
        if matrix[0][0] < old_f and len(artificial_variables) == 0:
            return 'Решение найти невозможно. Новое значение F менее оптимально.'

    if len(artificial_variables) > 0:
        return 'Решения не существует. В базисе осталась искусственная переменная'

    return 'Оптималььное решение получено'


def recount_T(matrix, indexes_of_artificial_variables):
    """ Считает линейную форму Т(х) - линейная форма, которую необходимо обратить в максимум. """
    T = [0 for _ in range(len(matrix[0]))]
    for i in indexes_of_artificial_variables:
        # T[0] -= symbol * matrix[i][0]
        for j in range(len(matrix[0])):
            T[j] -= matrix[i][j]
    return T


def dvoj_answer(matrix, indexes_of_variables, indexes_of_free_variables):
    writing = open(output_file_name, 'a')
    writing.write('\nРешение двойственной задачи\n')
    writing.close()
    print_answer(matrix, indexes_of_variables)
    writing = open(output_file_name, 'a')
    writing.write('\nРешение прямой задачи\n')
    for i in range(len(indexes_of_free_variables)):
        writing.write('x' + str(indexes_of_free_variables[i]) + ' = ' + str(matrix[0][i + 1]) + '\n')
    writing.write('F = ' + str(matrix[0][0]) + '\n')
    writing.close()



def print_answer(matrix, indexes_of_variables):
    """ Печатает ответ: чему равны xi и F """
    writing = open(output_file_name, 'a')
    for i in range(len(indexes_of_variables)):
        writing.write('x' + str(indexes_of_variables[i]) + ' = ' + str(matrix[i + 1][0]) + '\n')
    writing.write('F = ' + str(matrix[0][0]) + '\n')
    writing.close()


if __name__ == '__main__':
    print_starting_data()
    matrix, dvoj = reading_from_file()
    matrix, base_variables, free_variables, artificial_variables, indexes_of_artificial_variables = to_canonical(matrix)
    message = search_solution(matrix, base_variables, free_variables, artificial_variables, indexes_of_artificial_variables, dvoj)
    writing = open(output_file_name, 'a')
    writing.write(message)
    writing.close()
