import pandas as pd
import random

weekdays = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']


def get_empty_schedule(df_intervals: pd.DataFrame, week_length: int) -> dict:
    """
    Эта функция создает пустой шаблон расписания в виде дикта, в котором ключи это интервалы уроков
    в течение недели, а значения - дикт с ключом в виде номера кабинета со значением класса и учителя
    :param df_intervals: DataFrame
    :param week_length: int
    :return: dict
    """

    end_interval = df_intervals['end'].tolist()
    start_interval = df_intervals['begin'].tolist()
    intervals = []

    for i in range(week_length):
        for j in range(len(start_interval)):
            intervals.append(str(weekdays[i]) + ' ' + str(start_interval[j]) + ' ' + str(end_interval[j]))

    # Пустой шаблон расписания для заполнения
    population = dict(zip(intervals, [{} for _ in range(len(intervals))]))
    return population


def create_first_population(population: dict, academic_plan_df: pd.DataFrame, teachers_df: pd.DataFrame,
                            aud_type_df: pd.DataFrame, audiences_df: pd.DataFrame, number_of_days_in_week: int,
                            second_shift: int) -> dict:
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
        lst = list(population.keys())
        n = len(lst)
        interval_index = random.randrange(n)
        while ((interval_index % count_less_per_day) > end_of_the_shift) != (class_shift[row['class']] - 1):
            interval_index = random.randrange(n)
        # interval_index = random.randrange(n) // (second_shift + 1)) + 0.5 * \
        #                                count_less_per_day * (class_shift[row['class']] - 1)
        return lst[interval_index]

    second_shift = second_shift.get()
    # Замена NaN в 2, 3, 4... строках для каждого класса
    academic_plan_df['class'] = academic_plan_df['class'].fillna(method='ffill')
    # Распределение классов и интервалов на смены
    shift = False
    count_less_per_day = len(population) // number_of_days_in_week
    end_of_the_shift = count_less_per_day
    distinct_classes = sorted(academic_plan_df['class'].unique())
    class_shift = dict(zip(distinct_classes, [1 for _ in distinct_classes]))
    if second_shift:
        # Распределение классы по сменам
        for cl in class_shift:
            class_shift[cl] = int(shift) + 1
            shift = not shift
        # Конец первой смены
        end_of_the_shift = (end_of_the_shift - 1) // 2 #???

    # Развертка датафрейма для учителей
    for i, row in teachers_df.iterrows():
        teachers_df.iloc[i]['lesson'] = row['lesson'].split(', ')
    teachers_df = teachers_df.explode('lesson')
    for index, row in academic_plan_df.iterrows():
        # Количество данных уроков на неделе
        count = row['count']
        # Формирование ячейки расписания
        temp = [row['class'], row['lesson']]
        # Выбор типа аудитории
        required_type_audience = aud_type_df.loc[aud_type_df['lesson'] == row['lesson']].iloc[0]['type']
        possible_audiences = audiences_df.loc[audiences_df['type'] == required_type_audience]['audience'].to_list()
        random.shuffle(possible_audiences)
        # Выбор учителя
        possible_teachers = teachers_df.loc[teachers_df['lesson'] == row['lesson']]['teacher'].to_list()
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
