import pandas as pd


class AnalyticService():
    def __init__(self, data: pd.DataFrame, history: pd.DataFrame, sprints: pd.DataFrame):
        self.data: pd.DataFrame = data
        self.history: pd.DataFrame = history
        self.sprints: pd.DataFrame = sprints

        ''' Чистка 'history' dataframe '''
        self.history = self.history.reset_index()  # Сброс индекса
        columns = self.history.columns.tolist()  # Получаем текущий список колонок
        columns = columns[1:] + columns[:1]  # Перемещаем первую колонку в конец
        self.history.columns = columns  # Переупорядочиваем названия колонок
        if 'index' in history.columns:
            self.history.drop(columns=['index'], inplace=True)

        # TODO: final_table делать?

    # TODO: ИЗМЕНЯЕМ ЛИ SELF.DATA на FINAL_TABLE
    def calculate_metric_per_sprint(self):
        # Применяем расчёт метрики по каждому уникальному спринту
        sprint_metrics = {}
        for sprint_name in self.data['sprint_name'].unique():
            sprint_metrics[sprint_name] = self.__calculate_metric_per_sprint(self.data, sprint_name)

        # Добавляем результат в таблицу
        self.data['second_metric'] = self.data['sprint_name'].map(sprint_metrics)


    def __calculate_metric_per_sprint(self, df, sprint_name):
        # Фильтрация задач, относящихся к указанному спринту и имеющих статус "Создано"
        tasks_in_sprint = df[
            (df['sprint_name'] == sprint_name) &
            (df['status'] == 'Создано')
        ]
        # Суммирование estimation для задач спринта и деление на 3600
        metric = tasks_in_sprint['estimation'].sum() / 3600
        return metric