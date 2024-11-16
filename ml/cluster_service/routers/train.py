from fastapi import APIRouter, HTTPException
from models.model import ClusterModel
from models.schemas import InputData
import pandas as pd

import sys
import os

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter(prefix="/model/train", tags=["train"])
model = ClusterModel()

@router.post('/')
def train_model(input_data: InputData):
    try:
        model.load_data_from_json(input_data.dict())

        if model.df.empty:
            raise HTTPException(status_code=400, detail="Input data is empty.")

        model.preprocess()
        model.aggregate_features()
        scaled_features = model.scale_features(model.aggregated_features)
        trained_data = model.train_model(scaled_features)
        model.save_model()

        return {
            "message": "Model trained and saved successfully.",
            "clusters": trained_data.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))