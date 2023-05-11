import random
from turtle import pos


class Schedule:
    """
    Класс для представления расписания.

    Атрибуты
    --------
    number_of_days_in_week : int
        Количество учебных дней в неделе
    second_shift : bool
        Наличие второй смены

    df_teachers : pd.DataFrame
        Таблица с ФИО и специализацией учителей
    df_rings : pd.DataFrame
        Таблица с временем начала и конца каждого из уроков
    df_academic_plan : pd.DataFrame
        Учебный план в таблице из трех столбцов
            class : str
                класс
            lesson : str
                наименование дисциплины
            count : int
                количество данных уроков в неделю
    df_audiences_lessons : pd.DataFrame
        Таблица о необходимом для урока оборудовании
    df_audiences : pd.DataFrame
        Таблица о кабинетах и их оборудовании
    df_teachers_wishes : pd.DataFrame
        Таблица о пожеланиях учителей

    classes : tuple
        Упорядоченный кортеж с классами
    teachers : tuple
        упорядоченный кортеж с учителями
    intervals : tuple
        упорядоченный кортеж с интервалами для уроков
    audiences: tuple
        упорядоченный кортеж с аудиториями
    lessons: tuple
        упорядоченный кортеж с уроками

    schedule_dict : dict
        Текущий вариант расписания по шаблону
        {'WD HH:MM:SS-HH:MM:SS':
                            {'audience':
                                            {'class': str
                                            'lesson': str
                                            'teacher': str}
                            }
                            ...
        ...
        }

    schedule_list : list
        Текущий вариант расписания в виде прямоугольной таблицы
                | класс1 | класс2 | класс3 | класс4 |...
        --------
        Пн урок 1
        --------
        Пн урок 2
        --------
        ...

    Методы
    ------
    create_first_population(population):
        Создает черновой вариант расписания поверх пустого шаблона.
    classic_ga():
        Основная логика генетического алгоритма.
    classic_ga_target_function():
        Целевая функция генетического алгоритма. Выявление недостатков расписания.
    classic_ga_krossingover():
        Кроссинговер.
    classic_ga_inversion():
        Инверсия.
    classic_ga_mutation():
        Мутация.

    schedule_dict_to_table():
         Преобразует расписание в таблицу и заполняет атрибут schedule_list для вывода в приложение.
    """
    weekdays = ('ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС')

    def __init__(self, df_academic_plan, df_teachers, df_audiences_lessons, df_audiences, df_rings, df_teachers_wishes,
                 number_of_days_in_week, second_shift):
        """
        Устанавливает необходимые атрибуты для объекта Schedule.

        Параметры
        ---------
        number_of_days_in_week : int
            Количество учебных дней в неделе.
        second_shift : bool
            Наличие второй смены.

        df_teachers : pd.DataFrame
            Таблица с ФИО и специализацией учителей.
        df_rings : pd.DataFrame
            Таблица с временем начала и конца каждого из уроков.
        df_academic_plan : pd.DataFrame
            Учебный план в таблице из трех столбцов.
                class : str
                    Класс.
                lesson : str
                    Наименование дисциплины.
                count : int
                    Количество данных уроков в неделю.
        df_audiences_lessons : pd.DataFrame
            Таблица о необходимом для урока оборудовании.
        df_audiences : pd.DataFrame
            Таблица о кабинетах и их оборудовании.
        df_teachers_wishes : pd.DataFrame
            Таблица о пожеланиях учителей.

        classes : tuple
            Упорядоченный кортеж с классами.
        teachers : tuple
            Упорядоченный кортеж с учителями.
        intervals : tuple
            Упорядоченный кортеж с интервалами для уроков.

        schedule_dict : dict
            Текущий вариант расписания по шаблону.
            {'WD HH:MM:SS-HH:MM:SS':
                                {'audience':
                                                {'class': str
                                                'lesson': str
                                                'teacher': str}
                                }
                                ...
            ...
            }

        schedule_list : list
            Текущий вариант расписания в виде прямоугольной таблицы.
                    | класс1 | класс2 | класс3 | класс4 |...
            --------
            Пн урок 1
            --------
            Пн урок 2
            --------
            ...
        """

        # Данные школы
        self.number_of_days_in_week = number_of_days_in_week
        self.second_shift = second_shift

        # Входные дата фреймы
        self.df_teachers = df_teachers
        self.df_rings = df_rings
        self.df_academic_plan = df_academic_plan
        self.df_audiences_lessons = df_audiences_lessons
        self.df_audiences = df_audiences
        self.df_teachers_wishes = df_teachers_wishes
        # Вводные
        self.classes = sorted(tuple(cl for cl in df_academic_plan['class'].unique() if cl == cl),
                              key=lambda x: int(x[:-1]))
        self.teachers = sorted(tuple(cl for cl in df_teachers['teacher'].unique()))
        self.lessons = sorted(tuple(lesson for lesson in df_academic_plan['lesson'].unique()))
        self.audiences = sorted(tuple(str(audience) for audience in df_audiences['audience'].unique()))

        # Инициализация интервалов
        # Преобразование начала и конца уроков в списки
        end_interval = self.df_rings['end'].tolist()
        start_interval = self.df_rings['begin'].tolist()

        # Интервалы, в которые будут ставиться уроки
        intervals = []
        for i in range(self.number_of_days_in_week):
            for j in range(len(start_interval)):
                intervals.append(str(Schedule.weekdays[i]) + ' ' + str(start_interval[j]) + ' ' + str(end_interval[j]))
        self.intervals = tuple(intervals)

        # Пустой шаблон расписания для заполнения
        self.schedule_dict = dict(zip(self.intervals, [{} for _ in range(len(self.intervals))]))

        # Результат
        self.classic_ga()

    def create_first_population(self) -> None:
        """
        Создает расписание, в котором сохранена логика расписания между классами и кабинетами,
        но не между учителями. Сохраняет расписание поверх шаблона в schedule_dict.

        Возвращаемое значение
        ---------------------
        None
        """

        def get_interval() -> str:
            """
            Возвращает случайно выбранное время для урока в нужную смену.

            Возвращаемое значение
            ---------------------
            str
                строка вида 'WD HH:MM:SS-HH:MM:SS'
            """

            # Сохранили случайный интервал
            interval_index = random.randrange(len(self.intervals))

            # Пока не попали в смену
            while ((interval_index % count_less_per_day) > end_of_the_shift) != (class_shift[row['class']] - 1):
                interval_index = random.randrange(len(self.intervals))
            return self.intervals[interval_index]

        def is_lesson_at_this_interval(interval: str, sch_class: str) -> bool:
            """
            Функция возвращает True, если в interval у sch_class есть урок.
            False  в ином случае.

            Параметры
            ---------
            interval : str
                Временной промежуток.
            sch_class : str
                Класс, урок которого ищется.
            """
            for audience, dictionary in self.schedule_dict[interval].items():
                if dictionary['class'] == sch_class:
                    return True

            return False

        # Пустой шаблон расписания для заполнения
        self.schedule_dict = dict(zip(self.intervals, [{} for _ in range(len(self.intervals))]))

        # Замена NaN в 2, 3, 4... строках для каждого класса
        self.df_academic_plan['class'] = self.df_academic_plan['class'].fillna(method='ffill')

        # Замена NaN в 2, 3, 4... строках для каждого учителя, если введены пожелания
        if not self.df_teachers_wishes.empty:
            self.df_teachers_wishes['teacher'] = self.df_teachers_wishes['teacher'].fillna(method='ffill')

        # Распределение классов и интервалов на смены
        count_less_per_day = len(self.intervals) // self.number_of_days_in_week
        end_of_the_shift = count_less_per_day

        # Словарь {класс: смена}
        class_shift = dict(zip(self.classes, [1 for _ in self.classes]))

        # Распределение классов по сменам в случае наличия второй смены
        if self.second_shift:

            # Стандарт распределения классов на смены
            shift_standart = {1: False, 2: True, 3: True, 4: True, 5: False, 6: True, 7: True, 8: True, 9: False,
                              10: False, 11: False}
            for clas in class_shift.keys():
                class_shift[clas] = shift_standart[int(clas[:-1])] + 1

            # Конец первой смены
            end_of_the_shift = (end_of_the_shift - 1) // 2

        # Распаковка дата фрейма для учителей
        for i, row in self.df_teachers.iterrows():
            self.df_teachers.iloc[i]['lesson'] = row['lesson'].split(', ')
        self.df_teachers = self.df_teachers.explode('lesson')
        for index, row in self.df_academic_plan.iterrows():

            # Количество данных уроков на неделе
            count = row['count']

            # Формирование ячейки расписания
            temp = {"class": row['class'], "lesson": row['lesson']}

            # Выбор типа аудитории
            required_type_audience = self.df_audiences_lessons.loc[self.df_audiences_lessons['lesson']
                                                                   == row['lesson']].iloc[0]['type']
            possible_audiences = self.df_audiences.loc[self.df_audiences['type']
                                                       == required_type_audience]['audience'].to_list()
            # Перемешали, чтоб рассаживать в разные аудитории,
            # но исключить повторный выбор аудиторий за счет итерирования
            random.shuffle(possible_audiences)

            # Выбор учителя
            possible_teachers = self.df_teachers.loc[self.df_teachers['lesson'] == row['lesson']]['teacher'].to_list()
            temp["teacher"] = possible_teachers[random.randrange(len(possible_teachers))]

            # Для каждого из этого урока в данном классе
            for _ in range(count):

                # Флаг поиска аудитории и времени
                look_for_item = 1

                # Выбор случайного интервала
                interval = get_interval()
                # Занят ли этот интервал этим классом
                while is_lesson_at_this_interval(interval, temp['class']):
                    interval = get_interval()

                # Цикл поиска для текущего урока
                while look_for_item and count:

                    # Проход по подходящим аудиториям
                    for audience in possible_audiences:

                        # Если аудитория занята на это время
                        if audience in self.schedule_dict[interval]:

                            # Этим же классом
                            if self.schedule_dict[interval][audience]["class"] == temp["class"]:

                                # Тогда меняем время занятия
                                interval = get_interval()
                                # Занят ли этот интервал этим классом
                                while not is_lesson_at_this_interval(interval, temp['class']):
                                    interval = get_interval()
                                break
                            else:

                                # След. итерация, т.е. меняем аудиторию
                                continue

                        # Аудитория свободна
                        else:

                            # Занимаем ее
                            self.schedule_dict[interval][audience] = temp
                            look_for_item = 0
                            break

                    # Ни одна аудитория не оказалась свободной в это время
                    else:

                        # Меняем время занятия
                        interval = get_interval()
                        # Занят ли этот интервал этим классом
                        while is_lesson_at_this_interval(interval, temp['class']):
                            interval = get_interval()

    def create_first_population_randomly(self) -> None:
        """
        Создает расписание cлучайным образом.

        Возвращаемое значение
        ---------------------
        None
        """

        # Замена NaN в 2, 3, 4... строках для каждого класса
        self.df_academic_plan['class'] = self.df_academic_plan['class'].fillna(method='ffill')

        # Замена NaN в 2, 3, 4... строках для каждого учителя, если введены пожелания
        if not self.df_teachers_wishes.empty:
            self.df_teachers_wishes['teacher'] = self.df_teachers_wishes['teacher'].fillna(method='ffill')

        # Распаковка дата фрейма для учителей
        for i, row in self.df_teachers.iterrows():
            self.df_teachers.iloc[i]['lesson'] = row['lesson'].split(', ')
        self.df_teachers = self.df_teachers.explode('lesson')

        for interval in self.intervals:
            for sch_class in self.classes:
                # Случайный выбор аудитории
                audience = random.choice(self.audiences)

                # Случайный выбор урока
                lesson = random.choice(self.lessons)

                # Случайный выбор учителя
                teacher = random.choice(self.teachers)

                # Формирование ячейки расписания
                temp = {"class": sch_class, "lesson": lesson, "teacher": teacher}
                self.schedule_dict[interval][audience] = temp

    def fix_schedule(self) -> None:
        """
        Проверка расписания на консистентность и корректировка.
        1. Соответствие учебному плану
        2. Соответствие аудитории дисциплине
        3. Непротиворечивость расписания учителей
        4. Соответствие учителя дисциплине

        Непротиворечивость расписания классов -> учтена за счет модели решения задачи.

        Возвращаемое значение
        ---------------------
        None
        """
        # 1, 2, 4
        self.create_first_population()
        # 3
        self.fix_teacher_inconsistencies()

    def fix_teacher_inconsistencies(self) -> None:
        """
        Функция меняет местами ячейки расписания, которые нарушают логику учительского расписания.
        Если учитель ведет урок в двух классах одновременно, ячейка расписания меняется местами со следующей ячейкой
        текущего класса, чтобы накладки по учителям не было.

        Возвращаемое значение
        ---------------------
        None
        """
        def get_next_interval(interval, sch_class) -> str:
            """
            Возвращает время для следующего урока в нужную смену.

            Возвращаемое значение
            ---------------------
            str
                строка вида 'WD HH:MM:SS-HH:MM:SS'
            """
            # Распределение классов и интервалов на смены
            count_less_per_day = len(self.intervals) // self.number_of_days_in_week
            end_of_the_shift = count_less_per_day

            if self.second_shift:
                # Конец первой смены
                end_of_the_shift = (end_of_the_shift - 1) // 2

            # Сохранили случайный интервал
            interval_index = self.intervals.index(interval) + 1

            # Пока не попали в смену
            while ((interval_index % count_less_per_day) > end_of_the_shift) != (class_shift[sch_class] - 1):
                interval_index = (interval_index + 1) % len(self.intervals)
            return self.intervals[interval_index]

        def find_free_audience(interval: str, lesson: str) -> str:
            """
            Функция возвращает аудиторию, которая свободная в interval и подходит для проведения урока lesson.
            """
            # Выбор типа аудитории
            required_type_audience = self.df_audiences_lessons.loc[self.df_audiences_lessons['lesson']
                                                                   == lesson].iloc[0]['type']
            possible_audiences = self.df_audiences.loc[self.df_audiences['type']
                                                       == required_type_audience]['audience'].to_list()
            # Перемешали, чтоб рассаживать в разные аудитории,
            # но исключить повторный выбор аудиторий за счет итерирования
            random.shuffle(possible_audiences)
            for audience in self.schedule_dict[interval].keys():
                if audience in possible_audiences:
                    possible_audiences.remove(audience)
            if possible_audiences:
                return possible_audiences[0]
            else:
                return ''

        # Словарь {класс: смена}
        class_shift = dict(zip(self.classes, [1 for _ in self.classes]))

        # Распределение классов по сменам в случае наличия второй смены
        if self.second_shift:

            # Стандарт распределения классов на смены
            shift_standart = {1: False, 2: True, 3: True, 4: True, 5: False, 6: True, 7: True, 8: True, 9: False,
                              10: False, 11: False}
            for clas in class_shift.keys():
                class_shift[clas] = shift_standart[int(clas[:-1])] + 1

        for interval in self.intervals:
            teachers = dict()
            for audience, dictionary in self.schedule_dict[interval].copy().items():
                # Учитель ведет 2 урока одновременно
                if dictionary['teacher'] in teachers:
                    # Замена со следующим геном хромосомы
                    next_interval = get_next_interval(interval, dictionary['class'])
                    fixed = False
                    while not fixed:
                        if interval == next_interval:
                            break
                        # Ищем текущий класс в следующем интервале
                        for next_audience, next_dictionary in self.schedule_dict[next_interval].copy().items():
                            if dictionary['class'] == next_dictionary['class']:

                                if dictionary['teacher'] == next_dictionary['teacher']:
                                    # Если учитель совпал, не смысла менять местами эти уроки
                                    continue
                                elif next_dictionary['teacher'] in teachers:
                                    # Уроки разные, но этот учитель уже ведет урок
                                    break
                                else:
                                    # Нужно подобрать свободные аудитории для interval и next_interval
                                    aud = find_free_audience(interval, next_dictionary['lesson'])
                                    if not aud:
                                        # Если аудитория не нашлась
                                        continue

                                    next_aud = find_free_audience(next_interval, dictionary['lesson'])
                                    if not next_aud:
                                        # Если аудитория не нашлась
                                        continue


                                    # Меняем местами ячейки расписания
                                    self.schedule_dict[interval][aud] = next_dictionary
                                    self.schedule_dict[next_interval][next_aud] = dictionary
                                    if audience in self.schedule_dict[interval]:
                                        del self.schedule_dict[interval][audience]
                                    if next_audience in self.schedule_dict[next_interval]:
                                        del self.schedule_dict[next_interval][next_audience]
                                    teachers[next_dictionary['teacher']] = aud
                                    fixed = True
                                break
                        else:
                            # Следующая ячейка пуста
                            # Занимаем ее
                            next_aud = find_free_audience(next_interval, dictionary['lesson'])
                            if not next_aud:
                                # Если аудитория не нашлась
                                continue

                            self.schedule_dict[next_interval][next_aud] = dictionary
                            if audience in self.schedule_dict[interval]:
                                del self.schedule_dict[interval][audience]

                            fixed = True
                        next_interval = get_next_interval(next_interval, dictionary['class'])
                # Учитель ведет один урок в этот промежуток времени
                else:
                    # Сохраняем и аудиторию, чтобы в случае наложения расписания быстро найти место замены
                    teachers[dictionary['teacher']] = audience

    def classic_ga(self) -> None:
        """
        Основная логика классического генетического алгоритма:

        ПЕРВОЕ ПОКОЛЕНИЕ
        1. Первая популяция составляется случайным образом.
        2. Проверка расписания на консистентность и корректировка.
           Оценка приспособленности и запись значений функции для каждой особи.

        ВТОРОЕ И ПОСЛЕДУЮЩИЕ ПОКОЛЕНИЯ
        3. Генетические операторы
        2. Проверка расписания на консистентность и корректировка.
           Оценка приспособленности и запись значений функции для каждой особи.

        Возвращаемое значение
        ---------------------
        None
        """
        # Оценки приспособленности поколений
        score = list()

        # 1. Первая популяция составляется случайным образом.
        self.create_first_population_randomly()
        # 2. Проверка расписания на консистентность и корректировка.
        self.fix_schedule()
        # Оценка приспособленности и запись значений функции для каждой особи.
        cur_score = self.classic_ga_target_function(50, 50)
        score.append(cur_score)
        f = open("score.txt", "w")
        for sc in score:
            f.write(' '.join(list(map(str, sc))))
        f.close()

        self.schedule_dict_to_table(self)

    def modification_ga(self) -> None:
        # TODO исправить документацию
        """
        Основная логика классического генетического алгоритма:

        ПЕРВОЕ ПОКОЛЕНИЕ
        1. Первая популяция составляется случайным образом. --- Функция составления расписания рандомно.
        2. Проверка расписания на консистентность и корректировка. --- Функция исправления.
           Оценка приспособленности и запись значений функции для каждой особи.

        ВТОРОЕ И ПОСЛЕДУЮЩИЕ ПОКОЛЕНИЯ
        3. Генетические операторы
        2. Проверка расписания на консистентность и корректировка.
           Оценка приспособленности и запись значений функции для каждой особи.

        Возвращаемое значение
        ---------------------
        None
        """
        self.create_first_population()

        self.classic_ga_target_function()

    def classic_ga_target_function(self, window_fine: int, teacher_fine: int) -> tuple:
        """
        Целевая функция, оценивающая расписание. Сохраняет преобразованное расписание
        в schedule_dict и schedule_list.

        Возвращаемое значение
        ---------------------
        int
            Оценка приспособленности
        """
        self.schedule_list = self.schedule_dict_to_table(self)
        score = 0
        score_tuple = tuple()
        # TODO Разделить на подфункции
        # Окна у классов
        windows = set()

        # Конец смены
        end_of_the_shift = len(self.schedule_dict) // self.number_of_days_in_week
        if self.second_shift:
            # Конец первой смены
            end_of_the_shift = (end_of_the_shift - 1) // 2

        for ind_class, school_class in enumerate(self.schedule_list[0]):
            # Предыдущий интервал занят
            is_prev_lesson = False
            is_curr_lesson = False
            # Были ли сегодня уроки
            today_lessons = False
            score = 0
            for ind_interval, interval in enumerate(self.schedule_list):

                # Новый день или новая смена
                if ind_interval % (len(self.intervals) // self.number_of_days_in_week) == 0\
                        or ind_interval % (len(self.intervals) // self.number_of_days_in_week) == end_of_the_shift + 1:
                    is_prev_lesson = False
                    today_lessons = False
                else:
                    is_prev_lesson = is_curr_lesson

                is_curr_lesson = bool(interval[ind_class])

                # Предыдущий интервал занят, т.е. уроки продолжились или закончились
                if is_prev_lesson:
                    continue

                # Сейчас урока нет, до этого тоже
                elif not interval[ind_class]:
                    continue

                # Урока не было, сейчас есть, но уроки уже были сегодня
                elif today_lessons:
                    # Окно
                    score += window_fine
                    windows.add((ind_interval-1, ind_class))

                # Уроков не было, но начались
                else:
                    today_lessons = True
            score_tuple = score_tuple + (score,)
        # Учитель не ведет >1 урока в одно время

        # data_teachers = [['' for _ in self.teachers]
        #                  for _ in range(len(self.schedule_dict))]
        #
        # for interval_i, interval in enumerate(self.schedule_dict):
        #     for audience in self.schedule_dict[interval]:
        #         school_class = self.schedule_dict[interval][audience]['class']
        #         lesson = self.schedule_dict[interval][audience]['lesson']
        #         teacher = self.teachers.index(self.schedule_dict[interval][audience]['teacher'])
        #         item = str(lesson) + ' ' + str(school_class) + ' ' + str(audience)
        #         if not data_teachers[interval_i][teacher]:
        #             data_teachers[interval_i][teacher] = item
        #         else:
        #             # Учитель ведет >1 урока в одно время
        #             score += teacher_fine
        #             continue
        # Окна у учителей

        # TODO: система проверок на существование расписания под требования пользователя
        return score_tuple

    def classic_ga_krossingover(self, target_class1: str, target_class2: str) -> None:
        """
        Генетический оператор кроссинговера: обмен участками расписания двух классов.

        Параметры
        ---------
        target_class1 : str
            Хромосома, участок генов которой будет заменен на другой.
            Класс, расписание которого будет меняться.
        target_class2 : str
            Хромосома, участок генов которой будет заменен на другой.
            Класс, расписание которого будет меняться.
        """
        # Случайный интервал
        start_interval, end_interval = random.choice(list(self.intervals)), random.choice(list(self.intervals))
        start_interval_ind, end_interval_ind = self.intervals.index(start_interval), self.intervals.index(end_interval)
        if start_interval_ind > end_interval_ind:
            start_interval, end_interval = end_interval, start_interval
            start_interval_ind, end_interval_ind = end_interval_ind, start_interval_ind
        while start_interval_ind < end_interval_ind:

            # Извлекаем ячейки для первого и второго класса
            sch_dict1, sch_dict2 = {}, {}

            # TODO здесь могут быть накладки с кабинетами и учебным планом
            for audience, dictionary in self.schedule_dict[start_interval].items():

                # Извлекаем ячейку с target_class1
                if dictionary['class'] == target_class1:
                    sch_dict1[audience] = dictionary
                    del self.schedule_dict[start_interval][audience]
                # Извлекаем ячейку с target_class2
                if dictionary['class'] == target_class2:
                    sch_dict2[audience] = dictionary
                    del self.schedule_dict[start_interval][audience]

            # Ставим ячейки в новое место в таблице
            if sch_dict1:
                for audience, dictionary in sch_dict1:
                    sch_dict1[audience]['class'] = target_class2
                    self.schedule_dict[start_interval][audience] = sch_dict1[audience]
            if sch_dict2:
                for audience, dictionary in sch_dict2:
                    sch_dict2[audience]['class'] = target_class1
                    self.schedule_dict[start_interval][audience] = sch_dict2[audience]

            start_interval_ind += 1
            start_interval = self.intervals[start_interval_ind]

    def classic_ga_inversion(self, target_class: str) -> None:
        """
        Генетический оператор инверсии: разворачивает столбец расписания на 180 градусов
        от начала недели до случайно выбранной точки.

        Параметры
        ---------
        target_class : str
            Хромосома, ген в которой подвергнется мутации.
            Класс, расписание которого будет меняться.
        """
        # Начало участка обмена
        start_interval = self.intervals[0]
        start_interval_ind = 0

        # Случайный интервал, конец участка обмена
        end_interval = random.choice(list(self.intervals))
        end_interval_ind = self.intervals.index(end_interval)

        # Обход с концов интервала инверсии к его середине
        while start_interval_ind < end_interval_ind:
            # Извлекаем ячейки правого и левого конца интервала
            start_dict, end_dict = {}, {}

            # TODO здесь могут быть накладки с кабинетами

            # Извлекаем ячейку с target_class
            for audience, dictionary in self.schedule_dict[start_interval].items():
                if dictionary['class'] == target_class:
                    start_dict[audience] = dictionary
                    del self.schedule_dict[start_interval][audience]
                    break
            for audience, dictionary in self.schedule_dict[end_interval].items():
                if dictionary['class'] == target_class:
                    end_dict[audience] = dictionary
                    del self.schedule_dict[end_interval][audience]
                    break

            # Ставим ячейку в новое место в таблице
            if start_dict:
                for audience, dictionary in start_dict:
                    self.schedule_dict[end_interval][audience] = dictionary
            if end_dict:
                for audience, dictionary in end_dict:
                    self.schedule_dict[start_interval][audience] = dictionary

            start_interval_ind += 1
            end_interval_ind -= 1

    def classic_ga_mutation(self, target_class: str) -> None:
        """
        Генетический оператор мутации: изменение случайно выбранного гена(ячейки расписания).

        Параметры
        ---------
        target_class : str
            Хромосома, ген в которой подвергнется мутации.
            Класс, расписание которого будет меняться.
        """
        # Случайный интервал
        interval = random.choice(list(self.schedule_dict.keys()))
        mut = True  # Флаг

        while mut:
            for audience, dictionary in self.schedule_dict[interval].items():
                if dictionary['class'] == target_class:
                    # Промутировать ген
                    self.schedule_dict[interval][audience]['teacher'] = random.choice(self.teachers)
                    self.schedule_dict[interval][audience]['lesson'] = random.choice(
                        self.df_teachers.loc[
                            self.df_teachers['teacher'] == self.schedule_dict[interval][audience]['teacher']]
                        ['lesson'].to_list())
                    mut = False
                    break
            else:
                interval = random.choice(list(self.schedule_dict.keys()))

    @staticmethod
    def schedule_dict_to_table(self) -> list:
        """
        Преобразование расписания в прямоугольную таблицу.

        Возвращаемое значение
        ---------------------
        list
        """

        # Шаблон прямоугольной таблицы без заголовков строк и столбцов
        data_pupils = [['' for _ in range(len(self.classes))]
                       for _ in range(len(self.schedule_dict))]

        for interval_i, interval in enumerate(self.schedule_dict):
            for audience in self.schedule_dict[interval]:
                school_class = self.schedule_dict[interval][audience]['class']
                lesson = self.schedule_dict[interval][audience]['lesson']
                teacher = self.schedule_dict[interval][audience]['teacher']
                item = str(lesson) + '\n' + str(teacher) + '\n' + str(audience)
                data_pupils[interval_i][self.classes.index(school_class)] = item

        self.schedule_list = data_pupils
        return self.schedule_list
