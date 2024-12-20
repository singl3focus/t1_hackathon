# API

## Endpoints

**Особенности**:
- Стандарт времени ISO 8601

____

#### ```/healthy```
Принимает: Пустоту \
Отдаёт: 200 код

#### ```/sprint/add```
Принимает: 
```json
{
    "sprint_name": "Спринт 2024.3.1.NPP Shared Sprint",
	"sprint_status": "Закрыт",
	"sprint_start_date": "2024-07-03T19:00:00.44622Z",
	"sprint_end_date": "2024-07-16T19:00:00.44622Z",
	"entity_ids": [ 4327584 ]
}
```
Отдаёт: 200(400, 500) коды
```json
{
    "message": "Successful"
}
```

#### ```/sprint/update-status```
Принимает: 
```json
{
    "sprint_id": 1,
    "new_status": "Закрыт"
}
```
Отдаёт: 200(400, 500) коды
```json
{
    "message": "Successful"
}
```

#### ```/sprint/all```
Принимает: Пустоту \
Отдаёт: 200(400, 500) коды
```json
[
    {
        "sprint_id": 1,
        "sprint_name": "Спринт 2024.3.1.NPP Shared Sprint",
        "sprint_status": "Закрыт",
        "sprint_start_date": "2024-07-03T19:00:00.544622Z",
        "sprint_end_date": "2024-07-16T19:00:00.544622Z",
    },
    {
        "sprint_id": 2,
        "sprint_name": "Спринт 2024.2.2.NPP Shared Sprint",
        "sprint_status": "Закрыт",
        "sprint_start_date": "2024-10-04T17:00:00.544622Z",
        "sprint_end_date": "2024-11-16T18:00:00.544622Z",
    }
]
```

#### ```/sprint/task/all```
Принимает: Параметр **sprint_id** в запросе ***(/sprint/task/all?sprint_id=1)*** \
Отдаёт: 200(400, 500) коды
```json
[
    {
        "entity_id": 4327584,
        "area": "Система.ХранениеАртефактов",
        "type": "Задача",
        "status": "Закрыто",
        "state": "Normal",
        "priority": "Средний",
        "ticket_number": "PPAR-7200",
        "name": "[FЕ] Редактор шаблонов. Настройка обязательности атрибутов шаблона",
        "create_date": "2024-06-21T14:43:41.544622Z",
        "created_by": "А. К.",
        "update_date": "2024-08-13T14:50:31.562506Z",
        "updated_by": "В. Ю.",
        "parent_ticket_id": null,
        "assignee": "В. Ю.",
        "owner": "А. К.",
        "due_date": null,
        "rank": "0|qpthrc:",
        "estimation": null,
        "spent": null,
        "resolution": "Новая функциональность"
    }
]
```

#### ```/task/add```
Принимает: 
```json
{
    "entity_id": 4327586,
    "area": "Система.ХранениеАртефактов",
    "type": "Задача",
    "status": "Закрыто",
    "state": "Normal",
    "priority": "Средний",
    "ticket_number": "PPAR-7202",
    "name": "X2 Дополнительная настройка обязательности атрибутов шаблона",
    "create_date": "2024-06-21T17:43:41.11025Z",
    "created_by": "А. К.",
    "update_date": "2024-07-13T19:50:31.11025Z",
    "updated_by": "В. Ю.",
    "parent_ticket_id": 4318716,
    "assignee": "В. Ю.",
    "owner": "А. К.",
    "rank": "0|qpthrc:",
    "estimation": null,
    "spent": null,
    "resolution": "Новая функциональность"
  }
```
Отдаёт: 200(400, 500) коды
```json
{
    "message": "Successful"
}
```

#### ```/task/update-status```
Принимает: 
```json
{
    "entity_id": 4327584,
    "new_status": "Открыто"
}
```
Отдаёт: 200(400, 500) коды
```json
{
    "message": "Successful"
}
```

#### ```/task/update-state```
Принимает: 
```json
{
    "entity_id": 4327584,
    "new_state": "Good"
}
```
Отдаёт: 200(400, 500) коды
```json
{
    "message": "Successful"
}
```

#### ```/task/get-by-ticketnumber```
Принимает: Параметр **ticket_number** в запросе ***(/task/get-by-ticketnumber?ticket_number=PPAR-7200)*** \
Отдаёт: 200(400, 500) коды
```json
{
    "entity_id": 4327584,
    "area": "Система.ХранениеАртефактов",
    "type": "Задача",
    "status": "Закрыто",
    "state": "Normal",
    "priority": "Средний",
    "ticket_number": "PPAR-7200",
    "name": "[FЕ] Редактор шаблонов. Настройка обязательности атрибутов шаблона",
    "create_date": "2024-06-21T14:43:41.544622Z",
    "created_by": "А. К.",
    "update_date": "2024-08-13T14:50:31.562506Z",
    "updated_by": "В. Ю.",
    "parent_ticket_id": null,
    "assignee": "В. Ю.",
    "owner": "А. К.",
    "due_date": null,
    "rank": "0|qpthrc:",
    "estimation": null,
    "spent": null,
    "resolution": null
}
```

#### ```/task/changes/all```
Принимает: Параметр **entity_id** в запросе ***(/task/changes/all?entity_id=PPAR-4327586)*** 
```json
[
  {
    "entity_id": 4327586,
    "history_property_name": "Время решения 3ЛП ФАКТ",
    "history_date": "2024-09-08T12:17:06.680223Z",
    "history_version": 1,
    "history_change_type": "FIELD_CHANGED",
    "history_change": "<empty> -> 2024-09-10 11:17:06.680223"
  },
  {
    "entity_id": 4327586,
    "history_property_name": "Время решения (ФАКТ)",
    "history_date": "2024-09-09T11:11:06.680223Z",
    "history_version": 1,
    "history_change_type": "FIELD_CHANGED",
    "history_change": "<empty> -> 2024-09-10 11:17:06.680223"
  }
]   
```
Отдаёт: 200(400, 500) коды
```json
{
    "message": "Successful"
}
```

#### ```/tasks/add```
Принимает: 
```json
[
  {
    "entity_id": 4327586,
    "area": "Система.ХранениеАртефактов",
    "type": "Задача",
    "status": "Закрыто",
    "state": "Normal",
    "priority": "Средний",
    "ticket_number": "PPAR-7202",
    "name": "X2 Дополнительная настройка обязательности атрибутов шаблона",
    "create_date": "2024-06-21T17:43:41.11025Z",
    "created_by": "А. К.",
    "update_date": "2024-07-13T19:50:31.11025Z",
    "updated_by": "В. Ю.",
    "parent_ticket_id": 4318716,
    "assignee": "В. Ю.",
    "owner": "А. К.",
    "rank": "0|qpthrc:",
    "estimation": null,
    "spent": null,
    "resolution": "Новая функциональность"
  }
]   
```
Отдаёт: 200(400, 500) коды
```json
{
    "message": "Successful"
}
```

#### ```/tasks/changes/add```
Принимает: 
```json
[
  {
    "entity_id": 4327586,
    "history_property_name": "Время решения 3ЛП ФАКТ",
    "history_date": "2024-09-08T12:17:06.680223Z",
    "history_version": 1,
    "history_change_type": "FIELD_CHANGED",
    "history_change": "<empty> -> 2024-09-10 11:17:06.680223"
  },
  {
    "entity_id": 4327586,
    "history_property_name": "Время решения (ФАКТ)",
    "history_date": "2024-09-09T11:11:06.680223Z",
    "history_version": 1,
    "history_change_type": "FIELD_CHANGED",
    "history_change": "<empty> -> 2024-09-10 11:17:06.680223"
  }
]   
```
Отдаёт: 200(400, 500) коды
```json
{
    "message": "Successful"
}
```


## Data

### Таблица data_sprints (информация о спринтах):
- **sprint_name** – Название спринта. Пример: "Спринт 2024.3.1.NPP Shared Sprint" 
- **sprint_status** – Статус спринта. Пример: "Закрыт"
- **sprint_start_date** – Дата начала спринта. Пример: "2024-07-03 19:00:00.000000"
- **sprint_end_date** – Дата завершения спринта. Пример: "2024-07-16 19:00:00.000000"
- **entity_ids** – Список идентификаторов задач, входящих в спринт. Пример: "{4449728,4450628,4451563,4451929}"

### Таблица data_entities (информация о задачах):
- **entity_id** – Уникальный идентификатор задачи. Пример: 94297, 102481, 1805925
- **area** – Параметр, который отвечает за команду в данных (ранее указан как Workgroup). Пример: "Система.Таск-трекер", "Система.Ошибки"
- **type** – Тип задачи. Пример: "Дефект", "История"
- **status** – Текущий статус задачи. Пример: "Закрыто", "Тестирование"
- **state** – Состояние задачи. Пример: "Normal"
- **priority** – Приоритет задачи. Пример: "Средний", "Критический", "Высокий"
- **ticket_number** – Номер задачи. Пример: "PPTS-1965", "PPIN-1175"
- **name** – Название или описание задачи. Пример: "[FE] Бэклог. Кастомизация колонок.", "[ГенераторДокументов] Интеграция."
- **create_date** – Дата создания задачи. Пример: "2023-03-16 16:59:00.000000"
- **created_by** – Кто создал задачу. Пример: "А. К.", "А. З."
- **update_date** – Дата последнего обновления задачи. Пример: "2024-09-10 11:20:09.193785"
- **updated_by** – Кто последний раз обновлял задачу. Пример: "А. К.", "А. Е."
- **parent_ticket_id** – Номер родительской задачи (если задача является подзадачей). Пример: 72779, 3488105, NaN
- **assignee** – Кому назначена задача. Пример: "А. К.", "А. Е."
- **owner** – Автор задачи. Пример: "А. К.", "Я. П."
- **due_date** – Срок исполнения задачи. Пример: "NaN" (часто отсутствует)
- **rank** – Рейтинг или порядок задачи. Пример: "0|qzzywk:"
- **estimation** – Оценка времени выполнения задачи (в часах). Пример: 60.0, 432000.0
- **spent** – Время, затраченное на выполнение задачи. Пример: "NaN" (часто отсутствует)
- **esolution** – Резолюция задачи. Пример: "Готово", "Отклонено"

### Таблица data_history (история изменений задач):
- **entity_id** – Идентификатор задачи, к которой относятся изменения. Пример: 94297, 102481
- **history_property_name** – Параметр, который изменился. Пример: "Исполнитель", "Время решения (ФАКТ)"
- **history_date** – Дата изменения. Пример: "09.10.2024 11:17", "7/13/23 11:07"
- **history_version** – Версия изменения (номер итерации). Пример: 1.0, 3.0
- **history_change_type** – Тип изменения. Пример: "FIELD_CHANGED"
- **history_change** – Конкретное изменение. Пример: "user409017mail@mail.com -> user408045mail@mail.com", "<empty> -> 2024-09-10 11:17:06.680223"
