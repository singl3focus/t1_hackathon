from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import ast
from datetime import datetime, timedelta
from typing import List, Optional, Any

from service import AnalyticService

app = FastAPI()

# Подключение маршрутов
# app.include_router(predict.router)

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
    return {"message": "Welcome to the Clustering Service"}

@app.get("/process_data")
def read_root(request: ProcessDataRequest):
    data = pd.DataFrame([item.dict() for item in request.data])
    history = pd.DataFrame([item.dict() for item in request.history])
    sprints = pd.DataFrame([item.dict() for item in request.sprints])

    analytics = AnalyticService(data=data, history=history, sprints=sprints)

    return {"message": "Welcome to the Clustering Service"}