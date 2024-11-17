import pandas as pd
from datetime import timedelta
import json


class SprintAnalysis:
    def __init__(self, data: pd.DataFrame, history: pd.DataFrame, sprints: pd.DataFrame):

        self.data: pd.DataFrame = data
        self.history: pd.DataFrame = history
        self.sprints: pd.DataFrame = sprints

        # Data Preparation
        self._prepare_history()
        self._expand_sprints()
        self._merge_data()
        self._convert_dates()

    def _prepare_history(self):
        # Move "entity_id" to the first column
        self.history = self.history.reset_index()
        columns = self.history.columns.tolist()
        self.history.columns = columns[1:] + columns[:1]
        if 'index' in self.history.columns:
            self.history.drop(columns=['index'], inplace=True)
        self.history = self.history[
            self.history['entity_id'].apply(lambda x: isinstance(x, (int, float)))
        ]

    def _expand_sprints(self):
        # Split and expand entity_ids in sprints
        self.sprints['entity_ids'] = self.sprints['entity_ids'].apply(
            lambda x: x.strip('{}').split(',') if pd.notnull(x) else []
        )
        sprints_expanded = self.sprints.explode('entity_ids')
        sprints_expanded['entity_id'] = sprints_expanded['entity_ids'].astype(float)
        self.sprints = sprints_expanded

    def _merge_data(self):
        # Merge all tables
        self.data['entity_id'] = self.data['entity_id'].astype(float)
        self.history['entity_id'] = self.history['entity_id'].astype(float)
        data_sprints = pd.merge(self.data, self.sprints, on='entity_id', how='left')
        self.final_table = pd.merge(data_sprints, self.history, on='entity_id', how='left')

    def _convert_dates(self):
        self.sprints['sprint_start_date'] = pd.to_datetime(self.sprints['sprint_start_date'], errors='coerce')
        self.sprints['sprint_end_date'] = pd.to_datetime(self.sprints['sprint_end_date'], errors='coerce')
        self.final_table['history_date'] = pd.to_datetime(self.final_table['history_date'], errors='coerce')

    
    def calculate_first_metric_for_all_sprints(self):
        """
        Вычисляет первую метрику (К выполнению) для каждого спринта.
        
        :return: DataFrame с добавленной метрикой для каждого спринта.
        """
        self.data['first_metric'] = 0  # Инициализация метрики
        
        for _, sprint in self.sprints.iterrows():
            selected_sprint_entity_ids = sprint['entity_ids']
            if not isinstance(selected_sprint_entity_ids, list):
                selected_sprint_entity_ids = list(map(float, selected_sprint_entity_ids))
            
            tasks_in_sprint = self.data[
                (self.data['entity_id'].isin(selected_sprint_entity_ids)) &
                (self.data['status'] == 'Создано')
            ]

            # Суммирование estimation и деление на 3600
            first_metric_sum = tasks_in_sprint['estimation'].sum() / 3600

            # Обновление метрики в основном DataFrame
            self.data.loc[
                self.data['entity_id'].isin(selected_sprint_entity_ids),
                'first_metric'
            ] = first_metric_sum

        return self.data

    def calculate_daily_metrics(self):
        """
        Рассчитывает метрику "Снято" для каждого дня каждого спринта.
        
        :return: DataFrame с ежедневными метриками для каждого спринта.
        """
        # Условия для фильтрации задач
        valid_statuses = ["Закрыто", "Выполнено"]
        valid_resolutions = ["Отклонено", "Отменено инициатором", "Дубликат", "Отклонён исполнителем"]

        daily_metrics = []

        # Получение уникальных спринтов
        unique_sprints = self.data['sprint_name'].unique()

        # Цикл по каждому спринту
        for sprint_name in unique_sprints:
            # Фильтрация данных по текущему спринту
            sprint_data = self.data[self.data['sprint_name'] == sprint_name]

            # Определение диапазона дат спринта
            sprint_start_date = sprint_data['history_date'].min()
            sprint_end_date = sprint_data['history_date'].max()

            # Проход по дням спринта
            current_date = sprint_start_date
            while current_date <= sprint_end_date:
                # Фильтрация задач, относящихся к текущему дню и удовлетворяющих условиям
                tasks_cancelled_on_day = sprint_data[
                    (sprint_data['status'].isin(valid_statuses)) &
                    (sprint_data['resolution'].isin(valid_resolutions)) &
                    (sprint_data['history_date'] <= current_date)
                ]

                # Суммирование estimation и деление на 3600
                daily_metric = tasks_cancelled_on_day['estimation'].sum() / 3600

                # Добавление метрики в список
                daily_metrics.append({
                    'sprint_name': sprint_name,
                    'date': current_date,
                    'second_metric': round(daily_metric, 1)
                })

                # Переход к следующему дню
                current_date += pd.Timedelta(days=1)
        self.data['second_metrick'] = daily_metrics

        return self.data

    def calculate_daily_backlog(self):
        daily_backlog_metrics = []
        for _, sprint in self.sprints.iterrows():
            sprint_name = sprint['sprint_name']
            sprint_start_date = sprint['sprint_start_date']
            sprint_end_date = sprint['sprint_end_date']

            current_date = sprint_start_date
            while current_date <= sprint_end_date:
                backlog_change_pct = self._calculate_daily_backlog_change(sprint, current_date)
                daily_backlog_metrics.append({
                    'sprint_name': sprint_name,
                    'day': current_date,
                    'backlog_change_percentage': backlog_change_pct
                })
                current_date += timedelta(days=1)

        return pd.DataFrame(daily_backlog_metrics)

    def _calculate_daily_backlog_change(self, sprint, current_date):
        early_tasks_df = self.final_table[
            (self.final_table['history_date'].isna() |
             (self.final_table['history_date'] <= current_date)) &
            (self.final_table['type'] != 'Дефект')
        ]
        added_tasks_df = self.final_table[
            (self.final_table['history_date'] > current_date) &
            (self.final_table['type'] != 'Дефект')
        ]

        early_sum = early_tasks_df['estimation'].sum() / 3600
        added_sum = added_tasks_df['estimation'].sum() / 3600

        if early_sum > 0:
            return round((added_sum * 100) / early_sum, 1)
        elif added_sum > 0:
            return 100.0
        return 0.0

