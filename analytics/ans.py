import pandas as pd
from datetime import timedelta
import json


class SprintAnalysis:
    def __init__(self, json_file_path: json):
        
        self.data, self.history, self.sprints = self.json_to_dataframes()

        # Data Preparation
        self._prepare_history()
        self._expand_sprints()
        self._merge_data()
        self._convert_dates()

    def json_to_dataframes(json_file_path):
        """
        Преобразует JSON файл в три датафрейма: data, history и sprints.
        
        :param json_file_path: Путь к JSON файлу.
        :return: Кортеж из трех датафреймов (data, history, sprints).
        """
        # Чтение JSON файла
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Преобразование в датафреймы
        df_data = pd.DataFrame(data.get('data', []))
        df_history = pd.DataFrame(data.get('history', []))
        df_sprints = pd.DataFrame(data.get('sprints', []))
        
        return df_data, df_history, df_sprints

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


# Example usage
analysis = SprintAnalysis(
    data_path='data_for_spb_hakaton_entities1-Table 1.csv',
    history_path='history-Table 1.csv',
    sprints_path='sprints-Table 1.csv'
)

daily_backlog_df = analysis.calculate_daily_backlog()
