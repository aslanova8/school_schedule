import pandas as pd


def get_empty_schedule(df_intervals: pd.DataFrame, week_length: int) -> pd.DataFrame:
    '''
    Эта функция создает пустой шаблон расписания в виде дикта, в котором ключи это интервалы уроков
    в течение недели, а значения - дикт с ключом в виде номера кабинета со значением класса и учителя
    :param df_intervals: DataFrame
    :param week_length: int
    :return: dict
    '''
    weekdays = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
    end_interval = df_intervals['end'].tolist()
    start_interval = df_intervals['begin'].tolist()

    intervals = []
    audiences_dict = {}

    for i in range(week_length):
        for j in range(len(start_interval)):
            intervals.append(str(weekdays[i]) + ' ' + str(start_interval[j]) + ' ' + str(end_interval[j]))

    # Пустой шаблон расписания для заполнения
    population = dict(zip(intervals, [{} for i in range(len(intervals))]))
    return population

# TODO: def create_population
