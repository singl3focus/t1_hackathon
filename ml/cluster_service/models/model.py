import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from typing import Tuple
import pickle


class ClusterModel:
    def __init__(self, corr_threshold: float = 0.9, model_path: str = 'model_pipeline.pkl'):
        self.corr_threshold: float = corr_threshold
        self.model_path: str = model_path
        self.df: pd.DataFrame = pd.DataFrame()
        self.aggregated_features: pd.DataFrame = pd.DataFrame()
        self.model_pipeline: Pipeline = None

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

    def load_data_from_json(self, json_data: dict) -> None:
        self.df = pd.DataFrame(json_data["data"])
        if self.df.empty:
            raise ValueError("Loaded data is empty.")
        print("Data loaded successfully from JSON.")

    def preprocess(self) -> None:
        print("Columns before preprocessing:", self.df.columns)

        if self.df.empty:
            raise ValueError("Data not loaded. Please run load_data() first.")

        self.df = self.df.drop(columns=["sprintName", "blockedBy", "blocks", "priorityId", "assignee_summary"], errors="ignore")

        category_columns = self.df.select_dtypes(include='object').columns.drop(['sprintStartDate', 'sprintEndDate'], errors='ignore')
        for feature in category_columns:
            le = LabelEncoder()
            self.df[f'{feature}_encoded'] = le.fit_transform(self.df[feature].astype(str))
        self.df = self.df.drop(columns=category_columns)

        numeric_columns = self.df.select_dtypes(exclude='object').columns.drop(['sprintId'], errors='ignore')
        for col in numeric_columns:
            self.df[col] = self.df[col].fillna(self.df[col].mean())

        self.df = self.df.drop(columns=['sprintStartDate', 'sprintEndDate'], errors='ignore')

        # self._remove_highly_correlated_features()
        print("Columns after preprocessing:", self.df.columns)

        print("Data preprocessing complete.")

    def _remove_highly_correlated_features(self) -> None:
        corr_matrix = self.df.corr()
        col_corr = set()
        for i in range(len(corr_matrix.columns)):
            for j in range(i):
                if corr_matrix.iloc[i, j] >= self.corr_threshold:
                    colname = corr_matrix.columns[i]
                    col_corr.add(colname)
        self.df.drop(columns=list(col_corr), inplace=True)

    def aggregate_features(self) -> None:
        print("Columns before aggregation:", self.df.columns)

        if self.df.empty:
            raise ValueError("Data not preprocessed. Please run preprocess() first.")

        self.aggregated_features = self.df.groupby('sprintId').agg({
            'priority': ['mean', 'sum'],
            'storyPoint': ['mean', 'sum'],
            'issueLinks': ['mean', 'sum'],
            'votes': ['mean', 'sum'],
            'watchcount': ['mean', 'sum'],
            'subtasks': ['mean', 'sum'],
            'initialStoryPoint': ['mean', 'sum'],
            'totalNumberOfIssues': ['mean', 'sum'],
            'completedIssuesCount': ['mean', 'sum'],
            'puntedIssues': ['mean', 'sum'],
            'issuesNotCompletedInCurrentSprint': ['mean', 'sum'],
            'completedIssuesEstimateSum': ['mean', 'sum'],
            'NoOfDevelopers': ['mean', 'sum'],
            'SprintLength': ['mean', 'sum'],
            'issueType_encoded': 'sum',
            'status_issues_encoded': 'sum',
            'status_summary_encoded': ['mean', 'sum'],
            'sprintState_encoded': 'sum'
        }).reset_index()

        self.aggregated_features.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in self.aggregated_features.columns]
        print("Feature aggregation complete.")



    def train_model(self, scaled_features: pd.DataFrame) -> pd.DataFrame:
        if self.model_pipeline is None:
            n_components = min(scaled_features.shape[1], scaled_features.shape[0], 10)
            if n_components < 1:
                raise ValueError("Insufficient data for PCA. Ensure the input has enough samples and features.")

            self.model_pipeline = Pipeline([
                ('scaler', RobustScaler()),
                ('pca', PCA(n_components=n_components)),
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
        scaler: StandardScaler = self.model_pipeline.named_steps['scaler'] if self.model_pipeline else StandardScaler()
        scaled_data = scaler.fit_transform(data)
        return pd.DataFrame(scaled_data, columns=data.columns)

    def run(self) -> pd.DataFrame:
        self.load_data_from_json()
        self.preprocess()
        self.aggregate_features()
        scaled_features = self.scale_features(self.aggregated_features)
        result = self.train_model(scaled_features)
        self.save_model()
        return result
