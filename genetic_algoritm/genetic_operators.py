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


def create_first_population(population: dict, academic_plan_df: pd.DataFrame,
                            teachers_df: pd.DataFrame, aud_type_df: pd.DataFrame, audiences_df: pd.DataFrame) -> dict:
    for index, row in academic_plan_df.iterrows():
        temp = [row['class'], row['lesson']]
        # Выбор типа аудитории
        required_type_audience = aud_type_df.loc[aud_type_df['lesson'] == row['lesson']].iloc[0]['type']
        possible_audiences = audiences_df.loc[audiences_df['type'] == required_type_audience]['audience'].to_list()
        # Выбор учителя
        possible_teachers = teachers_df.loc[teachers_df['lesson'] == row['lesson']]['teacher'].to_list()
        temp.append(possible_teachers[random.randrange(len(possible_teachers))])
        # Выбор интервала
        interval = random.sample(population.items(), 1)[0][0]
        for i in possible_audiences:
            if i in population[interval]:
                continue
            else:
                population[interval][i] = temp
                break
        else:
            # Выбор другого интервала
            interval = random.sample(population.items(), 1)[0]
            # TODO: продумать как при смене интервала заново пробегаться по аудиториям
    return population
