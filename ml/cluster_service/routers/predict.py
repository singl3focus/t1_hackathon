from fastapi import APIRouter, HTTPException
from models.model import Model
from models.schemas import InputData
import pandas as pd

router = APIRouter(prefix="/model/predict", tags=["predict"])

# Инициализация модели
# Важно! Model требует входные данные (data, history, sprints, target) для инициализации.
# Предполагаем, что они будут загружены в процессе инициализации, либо через отдельный метод загрузки.
data_placeholder = pd.DataFrame()
history_placeholder = pd.DataFrame()
sprints_placeholder = pd.DataFrame()
target_placeholder = pd.Series()

cluster_model = Model(
    data=data_placeholder, 
    history=history_placeholder, 
    sprints=sprints_placeholder, 
    target=target_placeholder
)

@router.post("/")
async def predict_clusters(input_data: InputData):
    """
    Предсказывает кластеры на основе входных данных.
    """
    try:
        # Преобразование входных данных в DataFrame
        input_df = pd.DataFrame(input_data.dict()["data"])
        
        # Проверка на пустоту данных
        if input_df.empty:
            raise HTTPException(status_code=400, detail="Input data is empty.")
        
        # Загрузка данных в модель
        cluster_model.data = input_df
        
        # Предобработка данных
        aggregated_data = cluster_model.preprocess()

        # Разделение на успешные и неуспешные данные для кластеризации
        successful_sprints = aggregated_data[aggregated_data['target'] == 1]
        unsuccessful_sprints = aggregated_data[aggregated_data['target'] == 0]
        
        if successful_sprints.empty or unsuccessful_sprints.empty:
            raise HTTPException(status_code=400, detail="Not enough data for clustering.")

        # Кластеризация данных
        successful_clusters, unsuccessful_clusters = cluster_model.cluster_data(
            successful_sprints, unsuccessful_sprints
        )

        # Анализ кластеров
        cluster_analysis, highlighted_metrics = cluster_model.analyze_clusters(
            successful_clusters, unsuccessful_clusters
        )

        # Формирование ответа
        response = {
            "cluster_analysis": cluster_analysis,
            "highlighted_metrics": highlighted_metrics
        }
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
