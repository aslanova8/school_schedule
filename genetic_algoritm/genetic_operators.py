import random


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


    schedule_dict : dict
        Текущий вариант расписания по шаблону
        {'weekday start:end':
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
    get_empty_schedule():
        Возвращает пустой шаблон расписания.
    create_first_population(population):
        Создает черновой вариант расписания поверх пустого шаблона.
    ga_cycle():
        Основная логика генетического алгоритма.
    target_function():
        Целевая функция генетического алгоритма. Выявление недостатков расписания.
    schedule_dict_to_table():
         Преобразует расписание в таблицу.
    """
    weekdays = ('ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС')

    def __init__(self, df_academic_plan, df_teachers, df_audiences_lessons, df_audiences, df_rings, df_teachers_wishes,
                 number_of_days_in_week, second_shift):
        """
        Устанавливает необходимые атрибуты для объекта Schedule.

        Параметры
        ---------
        number_of_days_in_week : int
            количество учебных дней в неделе
        second_shift : bool
            наличие второй смены

        df_teachers : pd.DataFrame
            таблица с ФИО и специализацией учителей
        df_rings : pd.DataFrame
            таблица с временем начала и конца каждого из уроков
        df_academic_plan : pd.DataFrame
            учебный план в таблице из трех столбцов
                class : str
                    класс
                lesson : str
                    наименование дисциплины
                count : int
                    количество данных уроков в неделю
        df_audiences_lessons : pd.DataFrame
            таблица о необходимом для урока оборудовании
        df_audiences : pd.DataFrame
            таблица о кабинетах и их оборудовании
        df_teachers_wishes : pd.DataFrame
            Таблица о пожеланиях учителей

        classes : tuple
            упорядоченный кортеж с классами


        schedule_dict : dict
            текущий вариант расписания по шаблону
            {'weekday start:end':
                                {'audience':
                                                {'class': str
                                                'lesson': str
                                                'teacher': str}
                                }
                                ...
            ...
            }

        schedule_list : list
            текущий вариант расписания в виде прямоугольной таблицы
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

        # Результат
        self.ga_cycle()

    def get_empty_schedule(self) -> None:
        """
        Создает пустой шаблон расписания в виде дикта, в котором ключи это интервалы уроков
        в течение недели, а значения - дикт с ключом в виде номера кабинета
        со значением класса и учителя. Шаблон сохраняется в атрибут schedule_dict.

        {'weekday start:end':
                                {'audience':
                                                {'class': str
                                                'lesson': str
                                                'teacher': str}
                                }
                                ...
        ...
        }

        Возвращаемое значение
        ---------------------
        None
        """

        # Преобразуем начало и конец уроков в списки
        end_interval = self.df_rings['end'].tolist()
        start_interval = self.df_rings['begin'].tolist()

        # Интервалы, в которые будут ставиться уроки
        intervals = []
        for i in range(self.number_of_days_in_week):
            for j in range(len(start_interval)):
                intervals.append(str(Schedule.weekdays[i]) + ' ' + str(start_interval[j]) + ' ' + str(end_interval[j]))

        # Пустой шаблон расписания для заполнения
        population = dict(zip(intervals, [{} for _ in range(len(intervals))]))
        self.schedule_dict = population

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
            """

            # Сохранили случайный интервал
            intervals = list(self.schedule_dict.keys())
            interval_index = random.randrange(len(intervals))

            # Пока не попали в смену
            while ((interval_index % count_less_per_day) > end_of_the_shift) != (class_shift[row['class']] - 1):
                interval_index = random.randrange(len(intervals))
            return intervals[interval_index]

        # Замена NaN в 2, 3, 4... строках для каждого класса
        self.df_academic_plan['class'] = self.df_academic_plan['class'].fillna(method='ffill')

        # Замена NaN в 2, 3, 4... строках для каждого учителя
        self.df_teachers_wishes['teacher'] = self.df_teachers_wishes['teacher'].fillna(method='ffill')

        # Распределение классов и интервалов на смены
        second_shift = False
        count_less_per_day = len(self.schedule_dict) // self.number_of_days_in_week
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

    def ga_cycle(self) -> None:
        """
        Основная логика генетического алгоритма.

        Последовательно создаем расписание:
        1. Пустой шаблон
        2. Черновой вариант заполнения
        3. Целевая функция и преобразование расписания

        Возвращаемое значение
        ---------------------
        None
        """

        self.get_empty_schedule()
        self.create_first_population()

        self.target_function()

    def target_function(self) -> None:
        """
        Целевая функция, оценивающая расписание. Сохраняет преобразованное расписание
        в schedule_dict и schedule_list.

        Возвращаемое значение
        ---------------------
        None
        """
        self.schedule_list = self.schedule_dict_to_table(self)

        # Разделить на подфункции
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

            # Были ли сегодня уроки
            today_lessons = False

            for ind_interval, interval in enumerate(self.schedule_list):
                # Новый день
                if ind_interval % end_of_the_shift == 0:
                    is_prev_lesson = False
                    today_lessons = False
                # Предыдущий интервал занят
                if is_prev_lesson:
                    continue
                # Сейчас урока нет
                elif not interval[ind_class]:
                    continue
                # Урока не было, сейчас есть, но уроки уже были сегодня
                elif today_lessons:
                    # Окно
                    windows.add((ind_interval, ind_class))
                # Уроков не было, но начались
                else:
                    today_lessons = True

        # Учитель не ведет >1 урока в одно время

        data_teachers = [['' for _ in self.teachers]
                         for _ in range(len(self.schedule_dict))]

        for interval_i, interval in enumerate(self.schedule_dict):
            for audience in self.schedule_dict[interval]:
                school_class = self.schedule_dict[interval][audience]['class']
                lesson = self.schedule_dict[interval][audience]['lesson']
                teacher = self.teachers.index(self.schedule_dict[interval][audience]['teacher'])
                item = str(lesson) + ' ' + str(school_class) + ' ' + str(audience)
                if not data_teachers[interval_i][teacher]:
                    data_teachers[interval_i][teacher] = item
                else:
                    # Учитель ведет >1 урока в одно время
                    continue
        # Окна у учителей

        # TODO: система проверок на существование расписания под требования пользователя

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
