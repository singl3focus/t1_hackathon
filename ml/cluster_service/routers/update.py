from fastapi import APIRouter, HTTPException
from models.model import ClusterModel
from models.schemas import InputData

router = APIRouter(prefix="/model/update", tags=["update"])

model = ClusterModel()

@router.post("/")
def update_model(input_data: InputData):
    """
    Обновляет модель с использованием новых данных.
    """
    try:
        # Загружаем модель
        model.load_model()

        # Загружаем данные из JSON
        model.load_data_from_json(input_data.dict())

        if model.df.empty:
            raise HTTPException(status_code=400, detail="New data is empty.")

        # Предобработка данных
        model.preprocess()

        # Обновление модели
        updated_data = model.update_model(model.aggregated_features)

        return {
            "message": "Model updated successfully.",
            "updated_clusters": updated_data.to_dict(orient="records")
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
