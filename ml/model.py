import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from typing import Tuple

class ClusterModel:
    def __init__(self, data_path: str, corr_threshold: float = 0.9):
        self.data_path: str = data_path
        self.corr_threshold: float = corr_threshold
        self.df: pd.DataFrame = pd.DataFrame()
        self.aggregated_features: pd.DataFrame = pd.DataFrame()
        self.model_pipeline: Pipeline = Pipeline([])

    def load_data(self) -> None:
        self.df = pd.read_csv(self.data_path)
        print("Data loaded successfully.")

    def preprocess(self) -> None:
        if self.df.empty:
            raise ValueError("Data not loaded. Please run `load_data()` first.")

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

        self._remove_highly_correlated_features()
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
        if self.df.empty:
            raise ValueError("Data not preprocessed. Please run `preprocess()` first.")

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

    def scale_features(self) -> pd.DataFrame:
        if self.aggregated_features.empty:
            raise ValueError("Features not aggregated. Please run `aggregate_features()` first.")

        data_for_scaling = self.aggregated_features.drop(columns=['sprintId_'], errors='ignore')
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data_for_scaling)
        scaled_df = pd.DataFrame(scaled_data, columns=data_for_scaling.columns)
        print("Feature scaling complete.")
        return scaled_df

    def train_model(self, scaled_features: pd.DataFrame) -> pd.DataFrame:
        self.model_pipeline = Pipeline([
            ('scaler', RobustScaler()),
            ('pca', PCA(n_components=min(scaled_features.shape[1], 10))),
            ('kmeans', KMeans(n_clusters=2, random_state=42))
        ])

        scaled_features['cluster'] = self.model_pipeline.fit_predict(scaled_features)
        print("Model training complete.")
        return scaled_features

    def run(self) -> pd.DataFrame:
        self.load_data()
        self.preprocess()
        self.aggregate_features()
        scaled_features = self.scale_features()
        return self.train_model(scaled_features)
