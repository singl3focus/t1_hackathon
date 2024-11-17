import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler
import json
import pandas as pd



class Model:
    def __init__(self, data: pd.DataFrame, history: pd.DataFrame, sprints: pd.DataFrame, target: pd.DataFrame, 
                 threshold=0.1, n_clusters=3, random_state=42):
        self.data = data
        self.history = history
        self.sprints = sprints
        self.target = target

        self.preprocess()
        self.threshold = threshold
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.kmeans_successful = MiniBatchKMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        self.kmeans_unsuccessful = MiniBatchKMeans(n_clusters=self.n_clusters, random_state=self.random_state)

    def select_significant_metrics(self, metric_series):
        """
        Выбирает метрики, которые значительно отличаются от остальных.
        :param metric_series: Series с диапазонами метрик.
        :return: Список метрик.
        """
        if metric_series.empty:
            return []

        sorted_metrics = metric_series.sort_values(ascending=False)
        max_value = sorted_metrics.iloc[0]
        significant_metrics = sorted_metrics[sorted_metrics >= max_value * (1 - self.threshold)]
        return significant_metrics.index.tolist()

    def cluster_data(self, successful_data, unsuccessful_data):
        """
        Проводит кластеризацию успешных и неуспешных данных.
        :param successful_data: DataFrame с успешными спринтами.
        :param unsuccessful_data: DataFrame с неуспешными спринтами.
        :return: Два DataFrame с добавленными кластерами.
        """
        # Масштабирование данных
        features_successful = successful_data.drop(columns=["sprint_id", "success"])
        features_unsuccessful = unsuccessful_data.drop(columns=["sprint_id", "success"])
        scaled_successful = self.scaler.fit_transform(features_successful)
        scaled_unsuccessful = self.scaler.fit_transform(features_unsuccessful)

        # Кластеризация
        successful_clusters = self.kmeans_successful.fit_predict(scaled_successful)
        unsuccessful_clusters = self.kmeans_unsuccessful.fit_predict(scaled_unsuccessful)

        # Добавление кластеров в исходные данные
        successful_data = successful_data.copy()
        unsuccessful_data = unsuccessful_data.copy()
        successful_data["cluster"] = successful_clusters
        unsuccessful_data["cluster"] = unsuccessful_clusters

        return successful_data, unsuccessful_data

    def analyze_clusters(self, successful_data, unsuccessful_data):
        """
        Проводит анализ метрик кластеров для успешных и неуспешных данных.
        :param successful_data: DataFrame с кластерами успешных спринтов.
        :param unsuccessful_data: DataFrame с кластерами неуспешных спринтов.
        :return: Анализ кластеров и наиболее значимые метрики.
        """
        # Расчет средних значений и вариативности для каждого кластера
        successful_cluster_means = successful_data.groupby("cluster").mean()
        unsuccessful_cluster_means = unsuccessful_data.groupby("cluster").mean()
        successful_cluster_variability = successful_data.groupby("cluster").std()
        unsuccessful_cluster_variability = unsuccessful_data.groupby("cluster").std()

        # Различия между кластерами
        successful_diff = successful_cluster_means.max() - successful_cluster_means.min()
        unsuccessful_diff = unsuccessful_cluster_means.max() - unsuccessful_cluster_means.min()

        # Формирование итогового анализа
        cluster_analysis = {
            "Successful Cluster Mean Range": successful_diff,
            "Successful Cluster Variability": successful_cluster_variability.mean(),
            "Unsuccessful Cluster Mean Range": unsuccessful_diff,
            "Unsuccessful Cluster Variability": unsuccessful_cluster_variability.mean()
        }

        # Выбор наиболее выделяющихся метрик
        successful_top_metrics = self.select_significant_metrics(successful_diff)
        unsuccessful_top_metrics = self.select_significant_metrics(unsuccessful_diff)

        # Результат анализа
        highlighted_metrics = {
            "successful_sprints": successful_top_metrics,
            "unsuccessful_sprints": unsuccessful_top_metrics
        }

        return cluster_analysis, highlighted_metrics

    def load_data_from_json(self, json_data: dict) -> pd.DataFrame:
        self.df = pd.DataFrame(json_data["data"])
        if self.df.empty:
            raise ValueError("Loaded data is empty.")

        print("Data loaded successfully from JSON.")

        return self.df

    def save_to_json(self, data, file_name="highlighted_metrics.json"):
        """
        Сохраняет данные в JSON-файл.
        :param data: Словарь с данными для сохранения.
        :param file_name: Имя файла для сохранения.
        """
        with open(file_name, "w") as file:
            json.dump(data, file)

    def preprocess(self) -> pd.DataFrame:
    
        """
        Preprocessing + aggregating data
        
        **sprint_name** - Название спринта(по нему происходит агрегация)

        **mean_estimation, median_estimation, sum_estimation** - ['mean', 'median', 'sum']  
        # Средняя, медианная и суммарная оценка времени выполнения задачи (в часах)

        **avg_completion_time** - 'mean',  # Среднее время выполнения задач

        **completion_rate** - # Доля завершённых задач

        **rejected_rate** - # Доля отклонённых задач

        **defects** - # Количество дефектов

        **critical_tasks** - # Количество критических задач

        **task_count** - # Общее количество задач

        return: aggregated data

        """
        self.history = self.history.reset_index()  # Сброс индекса
        columns = self.history.columns.tolist()  # Получаем текущий список колонок
        columns = columns[1:] + columns[:1]  # Перемещаем первую колонку в конец
        self.history.columns = columns  # Переупорядочиваем названия колонок
        if 'index' in self.history.columns:
            self.history.drop(columns=['index'], inplace=True)

        # Разделение entity_ids в таблице sprints
        self.sprints['entity_ids'] = self.sprints['entity_ids'].apply(lambda x: x.strip('{}').split(',') if pd.notnull(x) else [])
        sprints_expanded = self.sprints.explode('entity_ids')
        sprints_expanded['entity_id'] = sprints_expanded['entity_ids'].astype(float)

        # Соединение data и sprints
        data_sprints = pd.merge(data, sprints_expanded, on='entity_id', how='left')

        # Соединение с history
        final_table = pd.merge(data_sprints, self.history, on='entity_id', how='left')

        data = final_table.copy()

        
        data['create_date'] = pd.to_datetime(data['create_date'], errors='coerce')
        data['update_date'] = pd.to_datetime(data['update_date'], errors='coerce')
        data['sprint_start_date'] = pd.to_datetime(data['sprint_start_date'], errors='coerce')
        data['sprint_end_date'] = pd.to_datetime(data['sprint_end_date'], errors='coerce')

        data['completion_time'] = (data['update_date'] - data['create_date']).dt.total_seconds() / 3600  # В часах

        # Метрики для каждого спринта
        agg_sprint_metricks = data.groupby('sprint_name').agg({
            'estimation': ['mean', 'median', 'sum'],  # Средняя, медианная и суммарная оценка
            'status': lambda x: (x.isin(['Закрыто', 'Готово']).sum()) / len(x),  # Доля завершённых задач
            'resolution': lambda x: (x == 'Отклонено').sum() / len(x),  # Доля отклонённых задач
            'completion_time': 'mean',  # Среднее время выполнения задач
            'type': lambda x: (x == 'Дефект').sum(),  # Количество дефектов
            'priority': lambda x: (x == 'Критический').sum(),  # Количество критических задач
            'entity_id': 'count'  # Общее количество задач
        }).reset_index()

        agg_sprint_metricks.columns = ['sprint_name', 'mean_estimation', 'median_estimation', 'sum_estimation',
                                'completion_rate', 'rejected_rate', 'avg_completion_time',
                                'defects', 'critical_tasks', 'task_count']
        
        agg_sprint_metricks['target'] = self.target
        return agg_sprint_metricks

