import pandas as pd
import random


class Schedule:
    weekdays = ('ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС')

    # Параметры
    number_of_days_in_week = 5
    second_shift = False

    # TODO можно ли убрать датафрейм и оставить только кортежи
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
        self.distinct_classes = sorted(tuple(cl for cl in df_academic_plan['class'].unique() if cl == cl),
                                       key=lambda x: int(x[:-1]))

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

        # Замена NaN в 2, 3, 4... строках для каждого класса
        self.df_academic_plan['class'] = self.df_academic_plan['class'].fillna(method='ffill')

        # Распределение классов и интервалов на смены
        second_shift = False
        count_less_per_day = len(population) // self.number_of_days_in_week
        end_of_the_shift = count_less_per_day

        class_shift = dict(zip(self.distinct_classes, [1 for _ in self.distinct_classes]))

        # Распределение классов по сменам
        if self.second_shift:
            for cl in class_shift:
                class_shift[cl] = int(second_shift) + 1
                second_shift = not second_shift

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
                        if audience in population[interval]:

                            # Этим же классом
                            if population[interval][audience]["class"] == temp["class"]:

                                # Тогда меняем время занятия
                                interval = get_interval()
                                break
                            else:

                                # След. итерация, т.е. меняем аудиторию
                                continue

                        # Аудитория свободна
                        else:

                            # Занимаем ее
                            population[interval][audience] = temp
                            look_for_item = 0
                            break

                    # Ни одна аудитория не оказалась свободной в это время
                    else:

                        # Меняем время занятия
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
        """
        Целевая функция, оценивающая расписание
        :param population:
        :return:
        """
        self.schedule_list = self.schedule_dict_to_table(self)

        # Окна у классов
        windows = set()

        # Конец смены
        end_of_the_shift = len(population) // self.number_of_days_in_week
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

        # Окна у учителей

        # Учитель не ведет >1 урока в одно время

        # TODO: система проверок на существование расписания под требования пользователя
        return population

    @staticmethod
    def schedule_dict_to_table(self) -> list:
        """
        Преобразование расписания в прямоугольную таблицу
        :return:
        """
        data = [['' for __ in range(len(self.distinct_classes))]
                for _ in range(len(self.schedule_dict))]

        for interval_i, interval in enumerate(self.schedule_dict):
            for audience in self.schedule_dict[interval]:
                school_class = self.schedule_dict[interval][audience]['class']
                lesson = self.schedule_dict[interval][audience]['lesson']
                teacher = self.schedule_dict[interval][audience]['teacher']
                item = str(lesson) + ' ' + str(teacher) + ' ' + str(audience)
                data[interval_i][self.distinct_classes.index(school_class)] = item

        self.schedule_list = data
        return self.schedule_list
