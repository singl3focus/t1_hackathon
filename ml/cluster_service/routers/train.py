from fastapi import APIRouter, HTTPException
from models.model import Model  # Используем ваш класс Model
from models.schemas import InputData
import pandas as pd
import sys
import os

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter(prefix="/model/train", tags=["train"])

# Заглушки для инициализации модели
data_placeholder = pd.DataFrame()
history_placeholder = pd.DataFrame()
sprints_placeholder = pd.DataFrame()
target_placeholder = pd.Series()

# Инициализация модели
model = Model(
    data=data_placeholder,
    history=history_placeholder,
    sprints=sprints_placeholder,
    target=target_placeholder
)

@router.post("/")
async def train_model(input_data: InputData):
    """
    Обучает модель на основе входных данных.
    """
    try:
        # Преобразование входных данных в DataFrame
        input_df = pd.DataFrame(input_data.dict()["data"])
        
        # Проверка входных данных
        if input_df.empty:
            raise HTTPException(status_code=400, detail="Input data is empty.")

        # Загрузка данных в модель
        model.data = input_df

        # Предобработка данных
        aggregated_data = model.preprocess()

        # Разделение данных на успешные и неуспешные спринты
        successful_sprints = aggregated_data[aggregated_data['target'] == 1]
        unsuccessful_sprints = aggregated_data[aggregated_data['target'] == 0]
        
        if successful_sprints.empty or unsuccessful_sprints.empty:
            raise HTTPException(status_code=400, detail="Not enough data for training.")

        # Кластеризация успешных и неуспешных данных
        successful_clusters, unsuccessful_clusters = model.cluster_data(
            successful_sprints, unsuccessful_sprints
        )

        # Сохранение модели (если требуется)
        # Здесь предполагается, что метод save_model() сохраняет состояния kmeans и другие параметры.
        model.save_to_json({
            "successful_clusters": successful_clusters.to_dict(orient="records"),
            "unsuccessful_clusters": unsuccessful_clusters.to_dict(orient="records")
        }, file_name="trained_model.json")

        return {
            "message": "Model trained and saved successfully.",
            "successful_clusters": successful_clusters.to_dict(orient="records"),
            "unsuccessful_clusters": unsuccessful_clusters.to_dict(orient="records"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during training: {str(e)}")
