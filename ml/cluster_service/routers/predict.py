from fastapi import APIRouter, HTTPException
from models.model import ClusterModel
from models.schemas import InputData

router = APIRouter(prefix="/model/predict", tags=["predict"])

# Инициализация модели
cluster_model = ClusterModel()

@router.post("/")
async def predict_clusters(input_data: InputData):
    """
    Предсказывает кластеры на основе входных данных.
    """
    try:
        # Загрузка данных
        cluster_model.load_data_from_json(input_data.dict())
        
        # Предобработка и прогнозирование
        cluster_model.preprocess()
        cluster_model.aggregate_features()
        scaled_features = cluster_model.scale_features(cluster_model.aggregated_features)
        result = cluster_model.train_model(scaled_features)

        cluster_info = result["cluster"].tolist()
        
        # Преобразование результата в JSON
        return {"clusters": cluster_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
