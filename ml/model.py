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

    def train_model(self, scaled_features: pd.DataFrame) -> pd.DataFrame:
        if self.model_pipeline is None:
            self.model_pipeline = Pipeline([
                ('scaler', RobustScaler()),
                ('pca', PCA(n_components=min(scaled_features.shape[1], 10))),
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
        self.load_data()
        self.preprocess()
        self.aggregate_features()
        scaled_features = self.scale_features(self.aggregated_features)
        result = self.train_model(scaled_features)
        self.save_model()
        return result
