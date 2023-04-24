import pandas as pd
import random
import math


class Schedule:
    weekdays = ('ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС')

    # Параметры
    number_of_days_in_week = 5
    second_shift = 0

    # TODO можно ли убрать датафрейм и оставить только корежи
    # Датафреймы с вводными для расписания
    df_teachers = pd.DataFrame
    df_audiences = pd.DataFrame
    df_audiences_lessons = pd.DataFrame
    df_rings = pd.DataFrame
    df_academic_plan = pd.DataFrame

    # Вводные для расписания
    distinct_classes = tuple

    # Заготовка расписания
    schedule_dict = dict
    schedule_list = list

    def __init__(self, df_academic_plan, df_teachers, df_audiences_lessons, df_audiences, df_rings,
                 number_of_days_in_week, second_shift):
        # Параметры
        self.number_of_days_in_week = number_of_days_in_week
        self.second_shift = second_shift

        # Датафреймы
        self.df_teachers = df_teachers
        self.df_rings = df_rings
        self.df_academic_plan = df_academic_plan
        self.df_audiences_lessons = df_audiences_lessons
        self.df_audiences = df_audiences

        # Вводные
        self.distinct_classes = sorted(tuple(cl for cl in df_academic_plan['class'].unique() if cl == cl))

        # Результат
        self.schedule_dict = self.ga_cycle()


    def get_empty_schedule(self) -> dict:
        """
        Эта функция создает пустой шаблон расписания в виде дикта, в котором ключи это интервалы уроков
        в течение недели, а значения - дикт с ключом в виде номера кабинета со значением класса и учителя

        :return: dict
        """

        end_interval = self.df_rings['end'].tolist()
        start_interval = self.df_rings['begin'].tolist()
        intervals = []

        # Интервалы, в которые будут ставиться уроки
        for i in range(self.number_of_days_in_week):
            for j in range(len(start_interval)):
                intervals.append(str(Schedule.weekdays[i]) + ' ' + str(start_interval[j]) + ' ' + str(end_interval[j]))

        # Пустой шаблон расписания для заполнения
        population = dict(zip(intervals, [{} for _ in range(len(intervals))]))
        return population

    def create_first_population(self, population: dict) -> dict:
        """
        Функция возвращает расписание, в котором сохранена логика расписания между классами и кабинетами,
        но не между учителями
        :param population: Пустое расписание

        :return: первый вариант расписания
        """

        def get_interval() -> str:
            """
            Возвращает случайно выбранное время для урока в нужную смену
            :return:
            """

            intervals = list(population.keys())
            n = len(intervals)
            interval_index = random.randrange(n)

            # Пока не попали в смену
            while ((interval_index % count_less_per_day) > end_of_the_shift) != (class_shift[row['class']] - 1):
                interval_index = random.randrange(n)
            return intervals[interval_index]

        # TODO вложенные словари
        # Замена NaN в 2, 3, 4... строках для каждого класса
        self.df_academic_plan['class'] = self.df_academic_plan['class'].fillna(method='ffill')

        # Распределение классов и интервалов на смены
        shift = False
        count_less_per_day = len(population) // self.number_of_days_in_week
        end_of_the_shift = count_less_per_day
        distinct_classes = sorted(self.df_academic_plan['class'].unique())
        class_shift = dict(zip(distinct_classes, [1 for _ in distinct_classes]))
        if self.second_shift:

            # Распределение классов по сменам
            for cl in class_shift:
                class_shift[cl] = int(shift) + 1
                shift = not shift

            # Конец первой смены
            end_of_the_shift = (end_of_the_shift - 1) // 2

        # Распаковка датафрейма для учителей
        for i, row in self.df_teachers.iterrows():
            self.df_teachers.iloc[i]['lesson'] = row['lesson'].split(', ')
        self.df_teachers = self.df_teachers.explode('lesson')
        for index, row in self.df_academic_plan.iterrows():

            # Количество данных уроков на неделе
            count = row['count']

            # Формирование ячейки расписания
            temp = [row['class'], row['lesson']]

            # Выбор типа аудитории
            required_type_audience = self.df_audiences_lessons.loc[self.df_audiences_lessons['lesson']
                                                                   == row['lesson']].iloc[0]['type']
            possible_audiences = self.df_audiences.loc[self.df_audiences['type']
                                                       == required_type_audience]['audience'].to_list()
            random.shuffle(possible_audiences)

            # Выбор учителя
            possible_teachers = self.df_teachers.loc[self.df_teachers['lesson'] == row['lesson']]['teacher'].to_list()
            temp.append(possible_teachers[random.randrange(len(possible_teachers))])
            for _ in range(count):
                look_for_item = 1
                interval = get_interval()
                while look_for_item and count:
                    for audience in possible_audiences:
                        if audience in population[interval]:
                            if population[interval][audience][0] == temp[0]:
                                interval = get_interval()
                                break
                            else:
                                continue
                        else:
                            population[interval][audience] = temp
                            look_for_item = 0
                            break
                    else:
                        interval = get_interval()

        return population

    def ga_cycle(self) -> dict:
        """
        Здесь основная логика генетического алгоритма
        :return:
        """
        population = self.get_empty_schedule()
        population = self.create_first_population(population)
        self.schedule_dict = population

        population = self.target_function(population)

        return population

    def target_function(self, population: dict) -> dict:
        self.schedule_list = self.schedule_dict_to_table(self)
        # Окна у классов
        # Окна у учителей
        # TODO: система проверок на существование расписания под требования пользователя
        return population

    @staticmethod
    def schedule_dict_to_table(self) -> list:
        """
        Преобразование расписания в прямоугольную таблицу
        :return:
        """
        temp = ['' for __ in range(len(self.distinct_classes))]
        data = [['' for __ in range(len(self.distinct_classes))]
                for _ in range(len(self.schedule_dict))]
        interval_num = 0
        for interval in self.schedule_dict:
            for audience in self.schedule_dict[interval]:
                school_class, lesson, teacher = [_ for _ in self.schedule_dict[interval][audience]]
                item = str(lesson) + ' ' + str(teacher) + ' ' + str(audience)
                data[interval_num][self.distinct_classes.index(school_class)] = item
            interval_num += 1

        self.schedule_list = data
        return self.schedule_list
