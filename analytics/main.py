from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from typing import List, Optional, Any
from analytic_service import AnalyticService  # Импортируем ваш класс

app = FastAPI(
    title="Sprint Analysis API",
    description="API for analyzing sprint performance metrics.",
    version="1.0.0"
)

# Определяем модели для обработки запросов
class DataItem(BaseModel):
    entity_id: Any
    area: Optional[str]
    type: Optional[str]
    status: Optional[str]
    state: Optional[str]
    priority: Optional[str]
    ticket_number: Optional[str]
    name: Optional[str]
    create_date: Optional[str]
    created_by: Optional[str]
    update_date: Optional[str]
    updated_by: Optional[str]
    parent_ticket_id: Optional[Any]
    assignee: Optional[str]
    owner: Optional[str]
    due_date: Optional[str]
    rank: Optional[Any]
    estimation: Optional[float]
    spent: Optional[float]
    workgroup: Optional[str]
    resolution: Optional[str]

    class Config:
        arbitrary_types_allowed = True


class HistoryItem(BaseModel):
    entity_id: Any
    history_property_name: Optional[str]
    history_date: Optional[str]
    history_version: Optional[int]
    history_change_type: Optional[str]
    history_change: Optional[str]


class SprintItem(BaseModel):
    sprint_name: Optional[str]
    sprint_status: Optional[str]
    sprint_start_date: Optional[str]
    sprint_end_date: Optional[str]
    entity_ids: Optional[List[int]]  # Должен быть список entity_ids


class ProcessDataRequest(BaseModel):
    data: List[DataItem]
    history: List[HistoryItem]
    sprints: List[SprintItem]


@app.get("/")
def root():
    """
    Приветственный маршрут.
    """
    return {"message": "Welcome to Sprint Analysis API"}


@app.post("/analyze")
def analyze_sprints(request: ProcessDataRequest):
    """
    Обрабатывает данные и возвращает метрики для анализа спринтов.
    """
    try:
        # Преобразование данных из запроса в pandas DataFrame
        data_df = pd.DataFrame([item.dict() for item in request.data])
        history_df = pd.DataFrame([item.dict() for item in request.history])
        sprints_df = pd.DataFrame([item.dict() for item in request.sprints])

        # Убедимся, что данные не пустые
        if data_df.empty or history_df.empty or sprints_df.empty:
            raise HTTPException(status_code=400, detail="Input data is empty or invalid.")

        # Инициализируем AnalyticService
        service = AnalyticService(data=data_df, history=history_df, sprints=sprints_df)

        # Расчет метрик
        service.calculate_metric_per_sprint()

        # Оценка успешности спринтов
        sprint_status = service.evaluate_sprint_success()

        # Возвращаем результат
        return {
            "message": "Sprint analysis completed successfully.",
            "sprint_status": sprint_status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Запуск через Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
