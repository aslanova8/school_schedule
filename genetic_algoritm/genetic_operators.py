import pandas as pd
import random


class Schedule:
    weekdays = ('ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС')

    # Создание атрибутов класса
    number_of_days_in_week = 5
    second_shift = 0

    # Датафреймы с вводными для расписания
    df_teachers = pd.DataFrame
    df_audiences = pd.DataFrame
    df_audiences_lessons = pd.DataFrame
    df_rings = pd.DataFrame
    df_academic_plan = pd.DataFrame

    schedule = dict

    def __init__(self, df_academic_plan, df_teachers, df_audiences_lessons, df_audiences, df_rings,
                 number_of_days_in_week, second_shift):
        self.df_teachers = df_teachers
        self.df_rings = df_rings
        self.df_academic_plan = df_academic_plan
        self.df_audiences_lessons = df_audiences_lessons
        self.df_audiences = df_audiences

        self.number_of_days_in_week = number_of_days_in_week
        self.second_shift = second_shift

        self.schedule = self.create_first_population(self.get_empty_schedule())

    def get_empty_schedule(self) -> dict:
        """
        Эта функция создает пустой шаблон расписания в виде дикта, в котором ключи это интервалы уроков
        в течение недели, а значения - дикт с ключом в виде номера кабинета со значением класса и учителя
        :param df_intervals: DataFrame
        :param week_length: int
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
        :param academic_plan_df: Данные для заполнения пустого шаблона
        :param teachers_df:
        :param aud_type_df:
        :param audiences_df:
        :param number_of_days_in_week:
        :param second_shift:
        :return: population - первый вариант расписания
        """

        def get_interval() -> str:
            """
            Возвращает случайно выбранное время для урока в нужную смену
            :return:
            """
            lst = list(population.keys())
            n = len(lst)
            interval_index = random.randrange(n)

            # Пока не попали в смену
            while ((interval_index % count_less_per_day) > end_of_the_shift) != (class_shift[row['class']] - 1):
                interval_index = random.randrange(n)
            # interval_index = random.randrange(n) // (second_shift + 1)) + 0.5 * \
            #                                count_less_per_day * (class_shift[row['class']] - 1)
            return lst[interval_index]

        #second_shift = second_shift.get()

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

        # Развертка датафрейма для учителей
        for i, row in self.df_teachers.iterrows():
            self.df_teachers.iloc[i]['lesson'] = row['lesson'].split(', ')
        self.df_teachers = self.df_teachers.explode('lesson')
        for index, row in self.df_academic_plan.iterrows():

            # Количество данных уроков на неделе
            count = row['count']

            # Формирование ячейки расписания
            temp = [row['class'], row['lesson']]

            # Выбор типа аудитории
            required_type_audience = self.df_audiences_lessons.loc[self.df_audiences_lessons['lesson'] == row['lesson']].iloc[0]['type']
            possible_audiences = self.df_audiences.loc[self.df_audiences['type'] == required_type_audience]['audience'].to_list()
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
