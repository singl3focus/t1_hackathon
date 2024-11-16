import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from typing import Tuple
import pickle


class ClusterModel:
    def __init__(self, csv_path: str = 'models/data/final_table.csv', corr_threshold: float = 0.9, model_path: str = 'model_pipeline.pkl'):
        """
        Инициализирует класс, загружает данные из CSV и производит предобучение.
        """
        self.corr_threshold: float = corr_threshold
        self.model_path: str = model_path
        self.df: pd.DataFrame = pd.DataFrame()
        self.aggregated_features: pd.DataFrame = pd.DataFrame()
        self.model_pipeline: Pipeline = None
        
        # Загрузка данных из CSV
        self.load_data_from_csv(csv_path)
        self.df = self.preprocess(self.df)
        self.train_model(self.scale_features(self.df))
        print("Model initialized and trained using data from CSV.")

    def load_data_from_csv(self, csv_path: str) -> None:
        """
        Загружает данные из CSV файла.
        """
        try:
            self.df = pd.read_csv(csv_path)
            if self.df.empty:
                raise ValueError("CSV file is empty.")
            print(f"Data successfully loaded from {csv_path}.")
        except FileNotFoundError:
            raise ValueError(f"CSV file not found at {csv_path}.")
    
    # Остальные методы класса без изменений...

    def load_model(self) -> None:
        """
        Загружает обученную модель из файла.
        """
        try:
            with open(self.model_path, 'rb') as f:
                self.model_pipeline = pickle.load(f)
            print(f"Model loaded successfully from {self.model_path}.")
        except FileNotFoundError:
            raise ValueError(f"Model file not found at {self.model_path}. Train the model first.")

    def save_model(self) -> None:
        if self.model_pipeline is None:
            raise ValueError("Model is not trained yet. Train the model before saving.")
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model_pipeline, f)
        print(f"Model saved to {self.model_path}.")

    def load_data_from_json(self, json_data: dict) -> pd.DataFrame:
        self.df = pd.DataFrame(json_data["data"])
        if self.df.empty:
            raise ValueError("Loaded data is empty.")

        print("Data loaded successfully from JSON.")

        return self.df        

    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        
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
        
        return agg_sprint_metricks

    def _remove_highly_correlated_features(self) -> None:
        corr_matrix = self.df.corr()
        col_corr = set()
        for i in range(len(corr_matrix.columns)):
            for j in range(i):
                if corr_matrix.iloc[i, j] >= self.corr_threshold:
                    colname = corr_matrix.columns[i]
                    col_corr.add(colname)
        self.df.drop(columns=list(col_corr), inplace=True)

    def train_model(self, scaled_features: pd.DataFrame) -> pd.DataFrame:
        if scaled_features.empty:
            raise ValueError("No features provided for training. Ensure data preprocessing and scaling steps are correct.")
        if self.model_pipeline is None:
            n_components = min(scaled_features.shape[1], scaled_features.shape[0], 10)
            if n_components < 1:
                raise ValueError("Insufficient data for PCA. Ensure the input has enough samples and features.")

            self.model_pipeline = Pipeline([
                ('scaler', RobustScaler()),
                ('kmeans', KMeans(n_clusters=2, random_state=42))
            ])
            scaled_features['cluster'] = self.model_pipeline.fit_predict(scaled_features)
        else:
            kmeans: KMeans = self.model_pipeline.named_steps['kmeans']
            kmeans.fit(scaled_features)
            scaled_features['cluster'] = kmeans.predict(scaled_features)
        print("Model training complete.")
        return scaled_features

    def update_model(self, new_data: pd.DataFrame) -> pd.DataFrame:
        if self.model_pipeline is None:
            raise ValueError("No trained model found. Train a model before updating.")

        scaled_data = self.scale_features(new_data)
        kmeans: KMeans = self.model_pipeline.named_steps['kmeans']
        kmeans.fit(scaled_data)
        scaled_data['cluster'] = kmeans.predict(scaled_data)
        print("Model updated with new data.")
        return scaled_data

    def scale_features(self, data: pd.DataFrame) -> pd.DataFrame:
        scaler = RobustScaler() if self.model_pipeline is None else self.model_pipeline.named_steps['scaler']
        scaled_data = scaler.fit_transform(data)
        return pd.DataFrame(scaled_data, columns=data.columns)


    # def run(self) -> pd.DataFrame:
    #     self.load_data_from_json()
    #     self.preprocess()
    #     scaled_features = self.scale_features(self.aggregated_features)
    #     result = self.train_model(scaled_features)
    #     self.save_model()
    #     return result
