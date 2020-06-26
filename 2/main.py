# lab2 исследование операций
# правила предпочтения:
# 1 - очередь FIFO - первым пришел, первым ушел
# 2 - длительность части технологического цикла, операции по которому осталось выполнить -> max

# содержание входного файла
# первая строка - номер правила
# производственные маршруты - для каждой детали новая строка
# пустая строка
# время обработки каждой детали на каждом станке

input_file_name = 'input.txt'
output_file_name = 'output.txt'


class Detail:
    def __init__(self, number, way, processing_time, event_recorder):
        """ Инициализация
        Номер детали, её технологический маршрут, время на каждом станке и обработчик событий задаются извне.
        Остальные параметры необходимы для работы модели (такие как количество пройденных станков и т.д.)"""
        self._number = number
        self._machine = None
        self._prev_id_le = 0
        self._way = way

        self._processing_time = processing_time
        self._queue_start_time = None
        self._operation_start_time = None

        self._event_recorder = event_recorder

        self._number_of_machine = 0

        self._done_tech_time = 0
        self._remain_time = sum(time for _, time in way)

    # свойства для удобной работы с полями класса
    @property
    def number(self): return self._number

    @property
    def machine(self): return self._machine

    @property
    def id_le_time(self):
        return self._prev_id_le + (self._processing_time.now() - self._queue_start_time)

    @property
    def remain_operation_time(self):
        _, time = self.next_operation
        return time - (self._processing_time.now() - self._operation_start_time)

    @property
    def way(self): return self._way

    @property
    def next_operation(self): return self._way[self._number_of_machine]

    @property
    def is_over(self): return self._number_of_machine >= len(self._way)

    @property
    def done_tech_time(self): return self._done_tech_time

    @property
    def remain_time(self): return self._remain_time

    @property
    def done_product_time(self): return self.done_tech_time + self.id_le_time

    # обработка состояний деталей: в очереди, на станке или закончил обработку на станке
    def on_queue(self):
        self._machine, _ = self.next_operation
        self._queue_start_time = self._processing_time.now()
        self._event_recorder((self._processing_time.now(), self._number, self._machine, 'q'))

    def load_on_machine(self):
        self._prev_id_le = self.id_le_time
        self._operation_start_time = self._processing_time.now()
        self._event_recorder((self._processing_time.now(), self._number, self._machine, 'b'))

    def remove_from_machine(self):
        _, time = self.next_operation
        self._done_tech_time += time
        self._remain_time -= time
        self._number_of_machine += 1
        self._event_recorder((self._processing_time.now(), self._number, self._machine, 'e'))


def fifo_rule(machine_queue, details):
    """ Возвращает индекс детали в соответствии с правилом предпочтения - очередь FIFO - первый пришел - первый ушёл """
    return 0


def max_remain_rule(machine_queue, details):
    """ Возвращает индекс детали, у которой остался длиннейший маршрут части технологического цикла """
    i, _ = max(enumerate(machine_queue), key=lambda detail: detail[1].remain_time)
    return i


class Model:
    """ Находим решение при помощи модели обработки всех деталей на станке """

    def model_procession(self, detail_tech_way, rule, event_recorder, queues_state_recorder):
        """ Обработка деталей на станках в соответствии с заданным правилом rule
            - detail_tech_way - список технологических маршрутов деталей (получен из функции reading)
            - rule - правило предпочтения (получено из функции reading)
            - event_recorder - записывает события, произошедшие с деталями
            - queues_state_recorder - записывает события очередей на станках
        """

        self._processing_time = ProcessingTime(0)  # начало отсчета общего времени обработки деталей
        self._queues_state_recorder = queues_state_recorder
        # инициализируем каждую деталь
        # записываем номер, технологический путь, время и регистратор событий
        self._details = tuple(Detail(i, way, self._processing_time, event_recorder)
                              for i, way in enumerate(detail_tech_way))
        self._rule = rule  # правило предпочтения (уже функция!!!)
        # создадим очереди деталей для каждого станка на основе технологических маршрутов и правила прдпочтения и
        # загрузим станки начальными деталями
        self._queues_for_each_machine = {}
        self._remained_details = set()
        self._update_queues(self._details)
        self._loading_on_machines(self._queues_for_each_machine.values())

        # обрабатываем все детали, пока не останется ни одной, не забываем о времени
        while len(self._remained_details) > 0:
            finished = self._remove_detail_from_machine()
            # обновляем очередь
            self._update_queues(finished)
            full_machines = set(detail.machine for detail in self._remained_details)
            free_machines = set(self._queues_for_each_machine.keys()) - full_machines
            self._loading_on_machines(self._queues_for_each_machine[machine] for machine in free_machines)

    def _update_queues(self, details):
        """ Обновляем очередь деталей для каждого станка.
        details - список деталей для загрузки в очередь. Используется при инициализации. """

        for detail in details:
            if not detail.is_over:
                # поставить деталь в очередь на обработку на станке
                detail.on_queue()
                self._queues_for_each_machine.setdefault(detail.machine, []).append(detail)

        for queue in self._queues_for_each_machine.values():
            queue.sort(key=lambda d: d.number)

        # записать состояние очередей после добавления деталей
        self._queues_state_recorder(self._processing_time.now(), self._queues_for_each_machine, "added")  #

    def _loading_on_machines(self, machines_queues):
        """ Загружаем указанные станки деталями из очередей """

        for queue in machines_queues:
            if len(queue) > 0:
                # обработка приоритетной детали из очереди
                detail = queue.pop(self._rule(queue, self._details))
                detail.load_on_machine()
                self._remained_details.add(detail)

        # записать состояние очередей после удаления деталей
        self._queues_state_recorder(self._processing_time.now(), self._queues_for_each_machine, "removed")  #

    def _remove_detail_from_machine(self):
        """ Удаляет обработанные детали со станков, возвращает список обработанных деталей """

        # минимальное время до окончания обработки детали
        minTime = min(detail.remain_operation_time for detail in self._remained_details)

        # получаем обработанные деталей
        finished = set(detail for detail in self._remained_details if detail.remain_operation_time == minTime)

        # исключаем обработанные детали из текущих
        self._remained_details -= finished

        # обновим время
        self._processing_time.increase(minTime)

        # и состояние
        for detail in finished:
            detail.remove_from_machine()

        return finished


class ProcessingTime:
    """ Время тик-так """

    def __init__(self, start=0): self._time = start

    def now(self): return self._time

    def increase(self, value): self._time += value


def reading():
    """ Чтение данных из файла
    Возвращаемые значения:

    - номер правила предпочтения

    - список, где i-ый элемент - список соответствующий производственному маршруту изделия с
    временем обработки детали на каждом станке
    Пример возвращаемого списка:

    [
    [('D', 1), ('A', 4), ('B', 3), ('C', 3)],
    [('A', 10), ('D', 5)],
    [('B', 3), ('D', 5), ('C', 5)],
    [('A', 1), ('B', 4)],
    [('B', 1), ('A', 6)],
    [('D', 1)],
    [('C', 1)],
    [('B', 6)]  ]   """

    reading = open(input_file_name, 'r')
    rule = int(reading.readline())
    machines = []
    for line in reading:
        if line.isspace():
            break
        machines.append(list(line.split()))
    times = []
    for line in reading:
        if line.isspace():
            break
        times.append(list(map(int, line.split())))
    reading.close()
    return rule, [list(zip(x, y)) for x, y in zip(machines, times)]


def print_result(ways, rule):
    model = Model()
    events = []
    states_of_queue = {}

    queues_state_recorder = generate_queue_state_recorder(states_of_queue)
    model.model_procession(ways, rule, lambda v: events.append(v), queues_state_recorder)

    machine_events = convert_to_output_machine_events(events)
    production_cycle_duration, *_ = events[-1]

    # вывод
    writer = open(output_file_name, 'w')
    if rule == fifo_rule:
        writer.write('Rule - FIFO\n\n')
    else:
        writer.write('Rule - the longest remaining part of the technological way\n\n')

    writer.write('Technological ways: \n')
    for i, way in enumerate(ways):
        writer.write(str(i))
        for j in way:
            writer.write(' -> ' + str(j))
        writer.write('\n')
    writer.write('\n')

    writer.write('Production cycle duration: ' + str(production_cycle_duration) + '\n\n')
    # вывод графика Ганта
    writer.write('Gantt chart:\n')

    def print_line():
        """ Функция для печати линейки
        Пример:
        0..............5..............10 """
        writer.write('\n')
        for n in range(0, production_cycle_duration + 1, 5):
            s = str(n)
            writer.write(s.ljust(15, '.'))
        writer.write('\n\n')

    print_line()
    message = ''
    for machine, timeline in machine_events:
        message += machine + ' '
        symbol = ' \' '
        prev_time = 0
        for time, event in timeline.items():
            if 'b' in event or 'e' in event:
                is_begin = 'b' in event
                detail = event['b' if is_begin else 'e']
                message += symbol * (time - prev_time)
                prev_time = time
                symbol = ' ' + str(detail) + ' ' if is_begin else ' \' '
        message += ' \' ' * (production_cycle_duration - prev_time)
        message += '\n'
    writer.write(message)
    print_line()

    writer.write('\nDetail\'s queues:\n')
    with open('output.txt', 'a', encoding='utf-8') as writer:
        write = lambda *args: print(*args, sep='', file=writer)
        print_line()
        for machine, view_queue in get_queues_states_view(states_of_queue, production_cycle_duration):
            write(f'{machine:2}', *view_queue[0])
            for line in view_queue[1:]:
                write('  ', *line)
            writer.write('*')
            for i in range(int(production_cycle_duration / 5)):
                writer.write('**************|')
            write('')
        print_line()

        write('Detail\'s downtime:')

        amount_of_details = len(set(detail for _, detail, *_ in events))
        details_downtime_on_machines = get_details_downtime_on_machines(machine_events, amount_of_details)
        writer.write('    ')
        for i in range(amount_of_details):
            writer.write(str(i) + '    ')
        writer.write('\n' + amount_of_details * 5 * '*' + '\n')
        for i in range(len(details_downtime_on_machines)):
            writer.write(details_downtime_on_machines[i][0] + ' * ')
            for j in range(amount_of_details):
                writer.write(str(details_downtime_on_machines[i][1][j]).ljust(5, ' '))
            writer.write('\n')

        writer.write('\nMachine\'s downtime:\n')

        machines_and_downtimes = get_machine_downtimes(machine_events)
        machines, downtimes = tuple(zip(*machines_and_downtimes))
        for i in range(len(machines)):
            writer.write(machines[i] + '   ' + str(downtimes[i]) + '\n')


def convert_to_output_machine_events(event_recorder):

    machine_events = {}
    for time, detail, machine, msg in event_recorder:
        timeline = machine_events.setdefault(machine, {})
        event = timeline.setdefault(time, {})
        if msg == 'q':
            event.setdefault(msg, []).append(detail)
        else:
            event[msg] = detail

    return sorted(machine_events.items(), key=lambda item: item[0])


def get_machine_downtimes(machine_events):
    machine_downtimes = {}
    for machine, timeline in machine_events:
        machine_ID = 0
        old_time = 0
        for time, event in timeline.items():
            if 'e' in event:
                old_time = time
            if 'b' in event:
                machine_ID += time - old_time
        machine_downtimes[machine] = machine_ID
    return sorted(machine_downtimes.items(), key=lambda item: item[0])


def generate_queue_state_recorder(states):
    """ Инициализация функции, которая будет записывать состояния очередей в контейнер. """

    def queue_state_recorder(time, machine_queues, message):
        if message == 'removed':
            for machine, queue in machine_queues.items():
                states.setdefault(time, {})[machine] = [d.number for d in queue]

    return queue_state_recorder


def get_queues_states_view(states, full_time):
    max_length_of_queue = {}
    for state in states.values():
        for machine, queue in state.items():
            if max_length_of_queue.setdefault(machine, 0) < len(queue):
                max_length_of_queue[machine] = len(queue)

    view_of_queues = {}
    for machine, length in max_length_of_queue.items():
        if length > 0:
            view_of_queues[machine] = tuple([' \' ']*full_time for _ in range(length))

    times = sorted(states.keys())
    converted = zip(times, [*times[1:], full_time], (states[t] for t in times))

    for time, new_time, machine_queues in converted:
        for machine, queue in machine_queues.items():
            for i, detail in enumerate(queue):
                view_of_queues[machine][i][time:new_time] = [' ' + str(detail) + ' '] * (new_time - time)

    return sorted(view_of_queues.items(), key=lambda item: item[0])


def get_details_downtime_on_machines(machine_events, amount_of_details):
    details_downtime_on_machines = {}
    for machine, timeline in machine_events:
        details_downtime_on_machines[machine] = [dict(machine_ID=0, old_time=None) for _ in range(amount_of_details)]
        for time, event in timeline.items():
            if 'q' in event:
                for detail in event['q']:
                    details_downtime_on_machines[machine][detail]['old_time'] = time
            if 'b' in event:
                params = details_downtime_on_machines[machine][event['b']]
                params['machine_ID'] += time - params['old_time']

    for machine, details in details_downtime_on_machines.items():
        details_downtime_on_machines[machine] = [params['machine_ID'] for params in details]

    return sorted(details_downtime_on_machines.items(), key=lambda v: v[0])


if __name__ == '__main__':
    rule, ways = reading()
    rule = fifo_rule if rule == 1 else max_remain_rule
    print_result(ways, rule)
