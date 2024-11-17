import pandas as pd


class AnalyticService:
    def __init__(self, data: pd.DataFrame, history: pd.DataFrame, sprints: pd.DataFrame):
        self.data: pd.DataFrame = data
        self.history: pd.DataFrame = history
        self.sprints: pd.DataFrame = sprints

        # Предобработка history
        self.history = self.history.reset_index(drop=True)
        columns = self.history.columns.tolist()
        columns = columns[1:] + columns[:1]
        self.history.columns = columns
        if 'index' in self.history.columns:
            self.history.drop(columns=['index'], inplace=True)

        # Приведение данных к корректным типам
        self._prepare_data()

    def _prepare_data(self):
        """
        Приведение типов и объединение данных.
        """
        # Разделение entity_ids в таблице sprints
        self.sprints['entity_ids'] = self.sprints['entity_ids'].apply(
            lambda x: x.strip('{}').split(',') if pd.notnull(x) else [])
        sprints_expanded = self.sprints.explode('entity_ids')
        sprints_expanded['entity_id'] = sprints_expanded['entity_ids'].astype(float)

        # Приведение entity_id к float
        self.data['entity_id'] = self.data['entity_id'].astype(float)
        self.history['entity_id'] = self.history['entity_id'].astype(float)

        # Объединение таблиц
        data_sprints = pd.merge(self.data, sprints_expanded, on='entity_id', how='left')
        self.data = pd.merge(data_sprints, self.history, on='entity_id', how='left')

    def calculate_metric_per_sprint(self):
        """
        Рассчитывает метрику для каждого спринта и добавляет ее в data.
        """
        sprint_metrics = {}
        for sprint_name in self.data['sprint_name'].unique():
            sprint_metrics[sprint_name] = self.__calculate_metric_for_sprint(self.data, sprint_name)

        # Добавляем рассчитанные метрики в таблицу
        self.data['second_metric'] = self.data['sprint_name'].map(sprint_metrics)

    def __calculate_metric_for_sprint(self, df: pd.DataFrame, sprint_name: str) -> float:
        """
        Внутренний метод для расчета метрики по конкретному спринту.
        """
        # Фильтрация задач по статусу "Создано" для указанного спринта
        tasks_in_sprint = df[
            (df['sprint_name'] == sprint_name) &
            (df['status'] == 'Создано')
        ]

        # Суммирование estimation и перевод в часы
        metric = tasks_in_sprint['estimation'].sum() / 3600
        return metric

    def get_sprint_metrics(self):
        """
        Возвращает рассчитанные метрики для всех спринтов.
        """
        self.calculate_metric_per_sprint()
        metrics = self.data[['sprint_name', 'second_metric']].drop_duplicates()
        return metrics

    def evaluate_sprint_success(self):
        """
        Оценивает успешность каждого спринта.
        """
        sprint_status = {}
        for sprint_name in self.data['sprint_name'].unique():
            status, issues = self._evaluate_sprint(sprint_name)
            sprint_status[sprint_name] = {
                "Статус": status,
                "Нарушения": issues
            }
        return sprint_status

    def _evaluate_sprint(self, sprint_name):
        """
        Внутренний метод для оценки успешности спринта.
        """
        sprint_data = self.data[self.data['sprint_name'] == sprint_name]

        if sprint_data.empty:
            return "Неуспешный", f"Спринт '{sprint_name}' отсутствует"

        # Проверка успешности
        violations = []
        total_tasks = sprint_data['estimation'].sum()

        # Проверка на количество задач
        if total_tasks == 0:
            violations.append("Нет задач в спринте")

        # Результат
        if violations:
            return "Неуспешный", violations
        return "Успешный", []
