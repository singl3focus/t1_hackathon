import pandas as pd


class SprintAnalyzer:
    def __init__(self, data_file, history_file, sprints_file):
        self.data = pd.read_csv(data_file, sep=';')
        self.history = pd.read_csv(history_file, sep=';')
        self.sprints = pd.read_csv(sprints_file, sep=';')

        self.preprocess_data()
        self.daily_metrics_df = None
        self.daily_backlog_metrics_df = None
        self.merged_df = None

    def preprocess_data(self):
        # Сдвиг колонок влево
        self.history = self.history.reset_index(drop=True)
        columns = self.history.columns.tolist()
        columns = columns[1:] + columns[:1]
        self.history.columns = columns
        if 'index' in self.history.columns:
            self.history.drop(columns=['index'], inplace=True)

        # Разделение entity_ids
        self.sprints['entity_ids'] = self.sprints['entity_ids'].apply(
            lambda x: x.strip('{}').split(',') if pd.notnull(x) else [])
        sprints_expanded = self.sprints.explode('entity_ids')
        sprints_expanded['entity_id'] = sprints_expanded['entity_ids'].astype(float)

        # Приведение entity_id к float
        self.data['entity_id'] = self.data['entity_id'].astype(float)
        self.history['entity_id'] = self.history['entity_id'].astype(float)

        # Соединение таблиц
        data_sprints = pd.merge(self.data, sprints_expanded, on='entity_id', how='left')
        self.data = pd.merge(data_sprints, self.history, on='entity_id', how='left')

    def calculate_daily_metrics(self):
        self.data['history_date'] = pd.to_datetime(self.data['history_date'], errors='coerce')
        valid_statuses = ["Закрыто", "Выполнено"]
        valid_resolutions = ["Отклонено", "Отменено инициатором", "Дубликат", "Отклонён исполнителем"]

        daily_metrics = []
        unique_sprints = self.data['sprint_name'].unique()

        for sprint_name in unique_sprints:
            sprint_data = self.data[self.data['sprint_name'] == sprint_name]
            sprint_start_date = sprint_data['history_date'].min()
            sprint_end_date = sprint_data['history_date'].max()

            current_date = sprint_start_date
            while current_date <= sprint_end_date:
                tasks_cancelled_on_day = sprint_data[
                    (sprint_data['status'].isin(valid_statuses)) &
                    (sprint_data['resolution'].isin(valid_resolutions)) &
                    (sprint_data['history_date'] <= current_date)
                ]
                daily_metric = tasks_cancelled_on_day['estimation'].sum() / 3600
                daily_metrics.append({
                    'sprint_name': sprint_name,
                    'date': current_date,
                    'second_metric': round(daily_metric, 1)
                })
                current_date += pd.Timedelta(days=1)

        self.daily_metrics_df = pd.DataFrame(daily_metrics)

    def calculate_backlog_metrics(self):
        self.sprints['sprint_start_date'] = pd.to_datetime(self.sprints['sprint_start_date'], errors='coerce')
        self.sprints['sprint_end_date'] = pd.to_datetime(self.sprints['sprint_end_date'], errors='coerce')

        daily_backlog_metrics = []

        def split_tasks_by_day(df, current_date):
            df['history_date'] = pd.to_datetime(df['history_date'], errors='coerce')
            early_tasks_df = df[
                (df['history_date'].isna() | (df['history_date'] <= current_date)) & (df['type'] != 'Дефект')]
            added_tasks_df = df[(df['history_date'] > current_date) & (df['type'] != 'Дефект')]
            return early_tasks_df, added_tasks_df

        def calculate_daily_backlog_change(data, sprint, current_date):
            early_tasks_df, added_tasks_df = split_tasks_by_day(data, current_date)
            early_sum = early_tasks_df['estimation'].sum() / 3600
            added_sum = added_tasks_df['estimation'].sum() / 3600
            if early_sum > 0:
                return round((added_sum * 100) / early_sum, 1)
            return 100.0 if added_sum > 0 else 0.0

        for _, sprint in self.sprints.iterrows():
            sprint_name = sprint['sprint_name']
            current_date = sprint['sprint_start_date']
            sprint_end_date = sprint['sprint_end_date']
            while current_date <= sprint_end_date:
                backlog_change_pct = calculate_daily_backlog_change(self.data, sprint, current_date)
                daily_backlog_metrics.append({
                    'sprint_name': sprint_name,
                    'day': current_date,
                    'backlog_change_percentage': backlog_change_pct
                })
                current_date += pd.Timedelta(days=1)

        self.daily_backlog_metrics_df = pd.DataFrame(daily_backlog_metrics)

    def merge_metrics(self):
        self.daily_backlog_metrics_df['day'] = pd.to_datetime(self.daily_backlog_metrics_df['day']).dt.date
        self.daily_metrics_df['date'] = pd.to_datetime(self.daily_metrics_df['date']).dt.date
        self.daily_metrics_df.rename(columns={'date': 'day'}, inplace=True)

        self.merged_df = pd.merge(
            self.daily_backlog_metrics_df,
            self.daily_metrics_df,
            on=['sprint_name', 'day'],
            how='inner'
        )
        self.merged_df.rename(columns={
            'first_metrick': "К выполнению",
            'second_metric': "Снято",
            'backlog_change_percentage': "Бэклог изменен с начала спринта на"
        }, inplace=True)

    def evaluate_sprints(self):
        def evaluate_sprint_success(df, sprint_name):
            sprint_data = df[df['sprint_name'] == sprint_name]
            if sprint_data.empty:
                return "Неуспешный", f"Спринт '{sprint_name}' отсутствует"
            violations = []
            sprint_data['К выполнению доля'] = sprint_data['К выполнению'] / \
                sprint_data[['К выполнению', 'Снято']].sum(axis=1)
            if (sprint_data['К выполнению доля'] > 0.2).any():
                violations.append("К выполнению > 20%")
            sprint_data['Снято доля'] = sprint_data['Снято'] / \
                sprint_data[['К выполнению', 'Снято']].sum(axis=1)
            if (sprint_data['Снято доля'] > 0.1).any():
                violations.append("Снято > 10%")
            if (sprint_data['Бэклог изменен с начала спринта на'] > 20).any():
                violations.append("Бэклог изменен > 20%")
            return "Успешный", [] if not violations else "Неуспешный", violations

        sprint_status = {}
        for sprint_name in self.merged_df['sprint_name'].unique():
            status, issues = evaluate_sprint_success(self.merged_df, sprint_name)
            sprint_status[sprint_name] = {"Статус": status, "Нарушения": issues}
        return sprint_status
