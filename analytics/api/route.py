from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from typing import List, Optional, Any

from sprint_analyzer import SprintAnalyzer  # Импорт класса SprintAnalyzer из вашего файла

app = FastAPI()

# Модели данных для запроса
class DataItem(BaseModel):
    entity_id: Any
    area: Optional[str]
    type: Optional[str]
    status: Optional[str]
    state: Optional[str]
    priority: Optional[str]
    ticket_number: Optional[str]
    name: Optional[str]
    create_date: Optional[datetime]
    created_by: Optional[str]
    update_date: Optional[datetime]
    updated_by: Optional[str]
    parent_ticket_id: Optional[Any]
    assignee: Optional[str]
    owner: Optional[str]
    due_date: Optional[datetime]
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
    history_date: Optional[datetime]
    history_version: Optional[int]
    history_change_type: Optional[str]
    history_change: Optional[str]

class SprintItem(BaseModel):
    sprint_name: Optional[str]
    sprint_status: Optional[str]
    sprint_start_date: Optional[datetime]
    sprint_end_date: Optional[datetime]
    entity_ids: Optional[List[int]]  # Должен быть список entity_ids

class ProcessDataRequest(BaseModel):
    data: List[DataItem]
    history: List[HistoryItem]
    sprints: List[SprintItem]

@app.get("/")
def read_root():
    """
    Приветственное сообщение
    """
    return {"message": "Welcome to the Sprint Analysis Service"}

@app.post("/process_data")
def process_data(request: ProcessDataRequest):
    """
    Обрабатывает данные о задачах, истории и спринтах.
    """
    try:
        # Преобразуем входные данные в DataFrame
        data = pd.DataFrame([item.dict() for item in request.data])
        history = pd.DataFrame([item.dict() for item in request.history])
        sprints = pd.DataFrame([item.dict() for item in request.sprints])

        # Инициализируем анализатор спринтов
        analyzer = SprintAnalyzer(data_file=None, history_file=None, sprints_file=None)

        # Подменяем данные в объекте класса
        analyzer.data = data
        analyzer.history = history
        analyzer.sprints = sprints

        # Выполняем предобработку
        analyzer.preprocess_data()

        # Рассчитываем метрики
        analyzer.calculate_daily_metrics()
        analyzer.calculate_backlog_metrics()

        # Объединяем данные
        analyzer.merge_metrics()

        # Оцениваем успешность спринтов
        sprint_status = analyzer.evaluate_sprints()

        return {
            "message": "Data processed successfully",
            "sprint_status": sprint_status
        }
    except Exception as e:
        return {
            "error": str(e)
        }
