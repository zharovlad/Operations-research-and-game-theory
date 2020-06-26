# Исследование операций лабораторная №6
# AX <= B
# Жаров

input_file_name = 'input3.txt'
output_file_name = 'output.txt'
const = 99999999


def reading_from_file():
    """ Возвращает систему ограничений и F в виде симплекс-таблицы и max или min """
    reading = open(input_file_name, 'r')
    s = reading.readline().split()
    m = reading.readline().split()[0]
    f = []
    for each in s:
        if m == 'max':
            f.append(-float(each))
        else:
            f.append(float(each))
    matrix = []
    for line in reading:
        s = line.split()
        array = []
        for i in range(len(s) - 2):
            array.append(float(s[i]))
        array.append(float(s[-1]))
        matrix.append(array)
    matrix.append(f)
    return matrix, m


def print_starting_data(matrix, m, indexes_of_free_variables, indexes_of_variables):
    """ Печатает входные данные: F и ограничения """
    writing = open(output_file_name, 'w')
    writing.write('F = ')
    if m == 'max':
        for i in range(len(matrix[0]) - 1):
            writing.write(' %.5f*' % -matrix[-1][i] + 'x' + str(indexes_of_free_variables[i]) + '  ')
        writing.write(' %.5f*' % -matrix[-1][-1] + 'b')
    else:
        for i in range(len(matrix[0]) - 1):
            writing.write(' %.5f*' % matrix[-1][i] + 'x' + str(indexes_of_free_variables[i]) + '  ')
        writing.write(' %.5f*' % matrix[-1][-1] + 'b')
    writing.write('  ->  ' + m + '\n\n')

    writing.write('Ограничения:\n')
    for i in range(len(indexes_of_variables)):
        for j in range(len(indexes_of_free_variables)):
            writing.write(('%.5f' % matrix[i][j]).center(10))
            writing.write('*x' + str(j) + ' +')
        writing.write(('<= %.5f' % matrix[i][-1]))
        writing.write('*b\n')
    writing.write('\n')
    writing.close()


def print_simplex_table(matrix, indexes_of_free_variables, indexes_of_variables):
    """ Печатает симплекс таблицу """
    writing = open(output_file_name, 'a')
    for i in range(len(indexes_of_free_variables)):
        writing.write('     x' + str(indexes_of_free_variables[i]) + '   ')
    writing.write('    b\n')

    for i in range(len(indexes_of_variables)):
         writing.write('x' + str(indexes_of_variables[i]))
         for j in range(len(matrix[0])):
             writing.write(('%.5f' % matrix[i][j]).center(10))
         writing.write('\n')

    writing.write('F ')
    for j in range(len(matrix[-1])):
        writing.write(('%.5f' % matrix[-1][j]).center(10))
    writing.write('\n\n')
    writing.close()


def print_answer(matrix, m, indexes_of_free_variables, indexes_of_variables):
    """ Печатает ответ: чему равны xi и F """
    writing = open(output_file_name, 'a')
    for i in indexes_of_free_variables:
        writing.write('x' + str(i) + ' = 0\n')
    for i in range(len(indexes_of_variables)):
        writing.write('x' + str(indexes_of_variables[i]) + ' = ' + str(matrix[i][-1]) + '\n')
    if m == 'min':
        matrix[-1][-1] = -matrix[-1][-1]
    writing.write('F = ' + str(matrix[-1][-1]) + '\n')
    writing.close()


def search_solution(matrix, m):
    """ Ищем решение """
    import copy
    indexes_of_free_variables = []  # здесь хранятся индексы свободных переменных
    indexes_of_variables = []       # а здесь базисных
    for i in range(len(matrix) - 1):
        indexes_of_variables.append(len(matrix[0]) + i)
    for i in range(len(matrix[i]) - 1):
        indexes_of_free_variables.append(i)

    # Печатаем входные данные
    print_starting_data(matrix, m, indexes_of_free_variables, indexes_of_variables)

    # печатаем симплекс таблицу на 0-ой итерации
    print_simplex_table(matrix, indexes_of_free_variables, indexes_of_variables)

    while True:
        # ищем разрешающий столбец
        # column - индекс разрешающего столбца

        min = const
        column = const
        for i, x in enumerate(matrix[-1]):
            if x < min and x < 0:
                min = x
                column = i
        if min == const:
            print_answer(matrix, m, indexes_of_free_variables, indexes_of_variables)
            return 'Оптимальное решение получено'

        # ищем разрешающую строку
        # string - индекс разрешающей строки

        string = const
        min = const
        for i, s in enumerate(matrix):
            try:
                if s[-1] / s[column] < min and s[column] > 0:
                    min = s[-1] / s[column]
                    string = i
            except:
                continue
        if min == const:
            return 'Оптимальное решение найти невозможно, так как F не ограничена на ОДР'

        # проверка на отрицательный x

        for i in range(len(indexes_of_variables)):
            if matrix[i][-1] < 0:
                return 'Оптимального решения нет, x' + str(i) + ' < 0'

        # изменим индексы
        indexes_of_variables[string], indexes_of_free_variables[column] = indexes_of_free_variables[column], \
                                                                            indexes_of_variables[string]
        # составляем новую симплексную таблицу

        # сохраним старую симплекс-таблицу
        old = copy.deepcopy(matrix)

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

        # печатаем симплекс таблицу после каждой итерации
        print_simplex_table(matrix, indexes_of_free_variables, indexes_of_variables)


if __name__ == '__main__':
    matrix, m = reading_from_file()
    message = search_solution(matrix, m)
    writing = open(output_file_name, 'a')
    writing.write(message)
    writing.close()
