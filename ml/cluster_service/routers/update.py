from fastapi import APIRouter, HTTPException
from models.model import Model  # Используем ваш класс Model
from models.schemas import InputData
import pandas as pd
import os
import sys

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter(prefix="/model/update", tags=["update"])

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
async def update_model(input_data: InputData):
    """
    Обновляет модель с использованием новых данных.
    """
    try:
        # Проверяем существование ранее сохраненной модели
        if not os.path.exists("trained_model.json"):
            raise HTTPException(status_code=404, detail="No existing model found to update.")

        # Загрузка данных из JSON (новые данные)
        new_data = pd.DataFrame(input_data.dict()["data"])

        if new_data.empty:
            raise HTTPException(status_code=400, detail="New data is empty.")

        # Объединение новых данных с существующими данными
        # Предполагается, что model.data содержит существующие данные
        model.data = pd.concat([model.data, new_data], ignore_index=True)

        # Предобработка объединенных данных
        aggregated_data = model.preprocess()

        # Разделение данных на успешные и неуспешные спринты
        successful_sprints = aggregated_data[aggregated_data['target'] == 1]
        unsuccessful_sprints = aggregated_data[aggregated_data['target'] == 0]

        if successful_sprints.empty or unsuccessful_sprints.empty:
            raise HTTPException(status_code=400, detail="Not enough data for updating the model.")

        # Обновление кластеров с учетом новых данных
        successful_clusters, unsuccessful_clusters = model.cluster_data(
            successful_sprints, unsuccessful_sprints
        )

        # Сохранение обновленной модели
        model.save_to_json({
            "successful_clusters": successful_clusters.to_dict(orient="records"),
            "unsuccessful_clusters": unsuccessful_clusters.to_dict(orient="records")
        }, file_name="trained_model.json")

        return {
            "message": "Model updated successfully.",
            "successful_clusters": successful_clusters.to_dict(orient="records"),
            "unsuccessful_clusters": unsuccessful_clusters.to_dict(orient="records"),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ValueError: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
