from math import inf
input_file_name = 'input1.txt'
output_file_name = 'output.txt'


def get_starting_data():
    """ Получаем данные из входного файла """
    returned_data = []

    with open(input_file_name, 'r') as r:
        method = int(r.readline())
        s = r.readline()
        s = s.split()
        a = [int(s[i]) for i in range(len(s))]
        s = r.readline()
        s = s.split()
        b = [int(s[i]) for i in range(len(s))]
        if sum(a) != sum(b):
            with open(output_file_name, 'w') as w:
                w.write('Ошибка ввода. Транспортная задача не сбалансирована')
            exit(1)
        returned_data = [a, b]

        if method == 2:
            s = r.readline()
            matrix = []
            try:
                for i in range(len(a)):
                    array = []
                    s = r.readline()
                    s = s.split()
                    for j in range(len(b)):
                        array.append([int(s[j]), i, j])
                    matrix.append(array)
            except:
                with open(output_file_name, 'w') as w:
                    w.write('Ошибка ввода. Размер матрицы не соответствует размеру векторов')
                exit(1)
            with open(output_file_name, 'w') as w:
                w.write('Исходная матрица\n')
                for i in matrix:
                    for j in i:
                        w.write(str(j[0]).center(5))
                    w.write('\n')

            preor = sort(matrix)

            returned_data.append(preor)
    return returned_data


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


def sort(matrix):
    """ Возвращает список с индексами матрицы, отсортированный по возрастанию значения в ячейке матрицы
    Пример:
    Входные данные:
    [
    [[10, 0, 0], [20, 0, 1]]
    [[15, 1, 0], [5, 1, 1]]
    ]
    Вернет:
    [[1, 1], [0, 0], [1, 0], [0, 1]] """
    preor = []
    for k in range(len(matrix) * len(matrix[0])):
        min = inf
        index = inf
        jindex = inf
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j][0] < min:
                    min = matrix[i][j][0]
                    index = i
                    jindex = j
        preor.append([matrix[index][jindex][1], matrix[index][jindex][2]])
        matrix[index].pop(jindex)

    return preor


def north_west_method(data):
    """ Находит допустимый опорный план методом северо-западного угла
    Выводит исходные данные, а также результат каждой итерации на экран """
    a = data[0]
    b = data[1]
    with open(output_file_name, 'w') as w:
        w.write('Метод северо-западного угла\n')
        w.write('a = ' + str(a) + '\n')
        w.write('b = ' + str(b) + '\n')
        result = [[0 for _ in range(len(b))] for __ in range(len(a))]
        print_iteration(result, a, b, w)
        i = 0
        j = 0
        while sum(a) != 0 and sum(b) != 0:
            temp = min(a[i], b[j])
            result[i][j] = temp
            b[j] -= temp
            a[i] -= temp
            if a[i] == 0:
                i += 1
            else:
                j += 1
            print_iteration(result, a, b, w)
    return


def min_elem_method(data):
    """ Находит допустимый опорный план методом минимального элемента
    Выводит исходные данные, а также результат каждой итерации на экран """
    a = data[0]
    b = data[1]
    c = data[2]
    with open(output_file_name, 'a') as w:
        w.write('Метод минимального элемента\n')
        w.write('a = ' + str(a) + '\n')
        w.write('b = ' + str(b) + '\n')
        result = [[0 for _ in range(len(b))] for __ in range(len(a))]
        print_iteration(result, a, b, w)
        k = 0
        while sum(a) != 0 and sum(b) != 0:
            i = c[k][0]
            j = c[k][1]
            temp = min(a[i], b[j])
            result[i][j] = temp
            b[j] -= temp
            a[i] -= temp
            k += 1
            print_iteration(result, a, b, w)
    return


def print_iteration(result, a, b, w):
    w.write('\n')
    for i in range(len(result)):
        for j in range(len(result[0])):
            w.write(str(result[i][j]).center(5))
        w.write('*' + str(a[i]).center(5))
        w.write('\n')
    w.write('*' * (5 * len(b) + 1) + '\n')
    for i in b:
        w.write(str(i).center(5))
    w.write('\n')


if __name__ == '__main__':
    data = get_starting_data()
    if len(data) == 3:
        min_elem_method(data)
    else:
        north_west_method(data)
