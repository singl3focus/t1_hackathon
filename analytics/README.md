# Аналитический раздел проекта

## Endpoint "/analyze" [POST]


Данные на прием:
```json
{
    "data": [
        {
            "entity_id": 1,
            "status": "Создано",
            "estimation": 3600,
            "create_date": "2023-11-01T00:00:00"
        },
        {
            "entity_id": 2,
            "status": "Создано",
            "estimation": 7200,
            "create_date": "2023-11-02T00:00:00"
        }
    ],
    "history": [
        {
            "entity_id": 1,
            "history_property_name": "status",
            "history_date": "2023-11-01T00:00:00"
        },
        {
            "entity_id": 2,
            "history_property_name": "status",
            "history_date": "2023-11-02T00:00:00"
        }
    ],
    "sprints": [
        {
            "sprint_name": "Sprint 1",
            "sprint_status": "Active",
            "sprint_start_date": "2023-11-01T00:00:00",
            "sprint_end_date": "2023-11-07T00:00:00",
            "entity_ids": [1, 2]
        }
    ]
}
```

Возврат: 
```json
{
    "message": "Sprint analysis completed successfully.",
    "sprint_status": {
        "Sprint 1": {
            "Статус": "Успешный",
            "Нарушения": []
        }
    }
}
```
