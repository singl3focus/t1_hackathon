-- +goose Up
-- +goose StatementBegin
-- Создание таблицы data_sprints (информация о спринтах)
CREATE TABLE data_sprints (
    sprint_id SERIAL PRIMARY KEY NOT NULL,
    sprint_name VARCHAR(255) NOT NULL,
    sprint_status VARCHAR(50) NOT NULL,
    sprint_start_date TIMESTAMP NOT NULL,
    sprint_end_date TIMESTAMP NOT NULL,
    entity_ids INTEGER[] NOT NULL  -- Массив идентификаторов задач, входящих в спринт
);

-- Создание таблицы data_entities (информация о задачах)
CREATE TABLE data_entities ( 
    entity_id INT PRIMARY KEY,  -- Уникальный идентификатор задачи
    area VARCHAR(255) NOT NULL,  -- Команда, ответственная за задачу
    type VARCHAR(50) NOT NULL,  -- Тип задачи (например, дефект или история)
    status VARCHAR(50) NOT NULL,  -- Статус задачи
    state VARCHAR(50) NOT NULL,  -- Состояние задачи
    priority VARCHAR(50) NOT NULL,  -- Приоритет задачи
    ticket_number VARCHAR(50) NOT NULL,  -- Номер задачи
    name TEXT NOT NULL,  -- Название задачи
    create_date TIMESTAMP NOT NULL,  -- Дата создания задачи
    created_by VARCHAR(255) NOT NULL,  -- Кто создал задачу
    update_date TIMESTAMP NOT NULL,  -- Дата последнего обновления задачи
    updated_by VARCHAR(255) NOT NULL,  -- Кто обновил задачу
    parent_ticket_id INT,  -- Идентификатор родительской задачи (если есть)
    assignee VARCHAR(255),  -- Кому назначена задача
    owner VARCHAR(255) NOT NULL,  -- Автор задачи
    due_date TIMESTAMP,  -- Срок исполнения задачи
    rank VARCHAR(255) NOT NULL,  -- Рейтинг задачи
    estimation FLOAT,  -- Оценка времени выполнения задачи (в часах)
    spent FLOAT,  -- Затраченное время на задачу (если есть)
    resolution VARCHAR(50)  -- Резолюция задачи (например, "Готово")
);

-- Создание таблицы data_history (история изменений задач)
CREATE TABLE data_history (
    entity_id INT NOT NULL,  -- Идентификатор задачи, к которой относятся изменения
    history_property_name VARCHAR(255) NOT NULL,  -- Параметр, который изменился
    history_date TIMESTAMP NOT NULL,  -- Дата изменения
    history_version FLOAT NOT NULL,  -- Версия изменения
    history_change_type VARCHAR(50) NOT NULL,  -- Тип изменения (например, FIELD_CHANGED)
    history_change TEXT NOT NULL,  -- Конкретное изменение
    PRIMARY KEY (entity_id, history_date, history_version),  -- Уникальный ключ для каждой версии изменения
    FOREIGN KEY (entity_id) REFERENCES data_entities(entity_id) ON DELETE CASCADE
);

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
-- Удаление таблицы data_history
DROP TABLE IF EXISTS data_history CASCADE;

-- Удаление таблицы data_entities
DROP TABLE IF EXISTS data_entities CASCADE;

-- Удаление таблицы data_sprints
DROP TABLE IF EXISTS data_sprints CASCADE;

-- +goose StatementEnd
