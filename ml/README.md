## 📮 API Эндпоинты

###  `/model/predict/` (POST)
- **Описание:** Обучает модель на новых данных и сохраняет её для дальнейшего использования.
- **Тело запроса (JSON):**
  ```json
  {
    "data": [
        {
            "entity_id": 94297,
            "area": "Система.Таск-трекер",
            "type": "Дефект",
            "status": "Закрыто",
            "state": "Normal",
            "priority": "Средний",
            "ticket_number": "PPTS-1965",
            "name": "[FE] Бэклог. Кастомизация колонок. Кастомизация для панелей \"спринты\" и  \"бэклоги\" зависима друг от друга",
            "create_date": "2023-03-16T16:59:00",
            "created_by": "А. К.",
            "update_date": "2024-09-10T11:20:09.193785",
            "updated_by": "А. К.",
            "parent_ticket_id": 72779,
            "assignee": "А. К.",
            "owner": "А. К.",
            "due_date": None,
            "rank": "0|qzzywk:",
            "estimation": 60,
            "spent": None,
            "workgroup": None,
            "resolution": "Готово"
        }
    ],
    "history": [
        {
            "entity_id": 94297,
            "history_property_name": "Время решения 3ЛП ФАКТ",
            "history_date": "2024-09-10T11:17:00",
            "history_version": 1,
            "history_change_type": "FIELD_CHANGED",
            "history_change": "<empty> -> 2024-09-10T11:17:06.680223"
        }
    ],
    "sprints": [
        {
            "sprint_name": "Спринт 2024.3.1.NPP Shared Sprint",
            "sprint_status": "Закрыт",
            "sprint_start_date": "2024-07-03T19:00:00",
            "sprint_end_date": "2024-07-16T19:00:00",
            "entity_ids": [
                4449728, 4450628, 4451563, 4451929, 4452033, 
                4452230, 4452511, 4452673, 4453981, 4454021, 94297
            ]
        }
    ],
    "target": [
        1
    ]
  }
 ```

```
### `/update/` (POST)
- **Описание:** Принимает данные и возвращает список кластеров для каждой строки входных данных.
- **Метод:** POST
- **Тело запроса (JSON):**
  ```json
  {
    "cluster_analysis": {
        "Successful Cluster Mean Range": {
            "metric_1": 0.5,
            "metric_2": 0.8
        },
        "Successful Cluster Variability": {
            "metric_1": 0.2,
            "metric_2": 0.3
        },
        "Unsuccessful Cluster Mean Range": {
            "metric_3": 1.2,
            "metric_4": 0.7
        },
        "Unsuccessful Cluster Variability": {
            "metric_3": 0.5,
            "metric_4": 0.6
        }
    },
    "highlighted_metrics": {
        "successful_sprints": ["metric_1", "metric_2"],
        "unsuccessful_sprints": ["metric_3", "metric_4"]
    }
  }
```