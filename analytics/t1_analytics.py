import pandas as pd
import numpy as np

# Загрузка данных
data = pd.read_csv('C:/Users/Alexe/OneDrive/Рабочий стол/data_for_spb_hakaton_entities1-Table 1.csv', sep=';')
history = pd.read_csv('C:/Users/Alexe/OneDrive/Рабочий стол/history-Table 1.csv', sep=';')
sprints = pd.read_csv('C:/Users/Alexe/OneDrive/Рабочий стол/sprints-Table 1.csv', sep=';')

# Парсинг дат
data['create_date'] = pd.to_datetime(data['create_date'], errors='coerce')
data['update_date'] = pd.to_datetime(data['update_date'], errors='coerce')
data['due_date'] = pd.to_datetime(data['due_date'], errors='coerce')

history['history_date'] = pd.to_datetime(history['history_date'], errors='coerce')

sprints['sprint_start_date'] = pd.to_datetime(sprints['sprint_start_date'], errors='coerce')
sprints['sprint_end_date'] = pd.to_datetime(sprints['sprint_end_date'], errors='coerce')

# Функция для разбора entity_ids в спринтах
def parse_entity_ids(x):
    if pd.isnull(x) or x == 'NaN':
        return []
    x = x.strip('{}')
    ids = x.split(',')
    ids = [int(id.strip()) for id in ids if id.strip()]
    return ids

sprints['entity_ids'] = sprints['entity_ids'].apply(parse_entity_ids)

# Сопоставление статусов с категориями
status_to_category = {
    'Создано': 'К выполнению',
    'Открыто': 'К выполнению',
    'Backlog': 'К выполнению',
    'Normal': 'К выполнению',  # Предположительно это аналог "Создано"
    'В работе': 'В работе',
    'Development': 'В работе',
    'Тестирование': 'В работе',
    'Review': 'В работе',
    'Закрыто': 'Сделано',
    'Готово': 'Сделано',
    'Сделано': 'Сделано',
    'Отклонено': 'Снято',
    'Отменено инициатором': 'Снято',
    'Дубликат': 'Снято',
    'Отклонен исполнителем': 'Снято',
    'Rejected by performer': 'Снято',
}

# Обработка каждого спринта
for index, selected_sprint in sprints.iterrows():
    print(f"\nОбработка спринта: {selected_sprint['sprint_name']}")
    
    sprint_tasks = selected_sprint['entity_ids']
    sprint_start = selected_sprint['sprint_start_date']
    sprint_end = selected_sprint['sprint_end_date']
    
    # Генерация списка дат спринта
    sprint_dates = pd.date_range(start=sprint_start, end=sprint_end, freq='D')
    
    # Задачи из выбранного спринта
    tasks_in_sprint = data[data['entity_id'].isin(sprint_tasks)].copy()
    tasks_in_sprint = tasks_in_sprint[['entity_id', 'estimation', 'type', 'status', 'resolution', 'create_date']]
    
    # История изменений статусов задач в спринте
    status_history = history[history['entity_id'].isin(sprint_tasks)]
    status_history = status_history[status_history['history_property_name'] == 'Статус']
    status_history = status_history[['entity_id', 'history_date', 'history_change']]
    
    # Инициализация DataFrame для хранения ежедневных показателей
    daily_metrics = []

    for current_date in sprint_dates:
        print(f"\nДата: {current_date.strftime('%Y-%m-%d')}")
        
        # Отбираем задачи, созданные до текущей даты
        tasks_current = tasks_in_sprint[tasks_in_sprint['create_date'] <= current_date]
        current_task_ids = tasks_current['entity_id'].tolist()
        
        # История изменений статусов до текущей даты
        status_history_current = status_history[status_history['history_date'] <= current_date]
        
        # Последнее изменение статуса перед текущей датой
        status_history_current = status_history_current.sort_values(['entity_id', 'history_date'])
        last_status_changes = status_history_current.groupby('entity_id').tail(1)
        
        # Задачи без изменений статуса до текущей даты
        tasks_with_status_changes = set(last_status_changes['entity_id'].unique())
        tasks_without_status_changes = set(current_task_ids) - tasks_with_status_changes
        
        # Для задач без изменений считаем начальный статус "Создано"
        tasks_without_status_changes_df = pd.DataFrame({'entity_id': list(tasks_without_status_changes)})
        tasks_without_status_changes_df['new_status'] = 'Создано'
        
        # Объединяем данные о статусах
        status_df = pd.concat([last_status_changes[['entity_id', 'history_change']].rename(columns={'history_change': 'new_status'}), tasks_without_status_changes_df], ignore_index=True)
        
        # Объединение с задачами для получения оценок
        status_df = status_df.merge(tasks_current[['entity_id', 'estimation', 'type', 'status', 'resolution']], on='entity_id', how='left')
        
        # Функция для извлечения нового статуса
        def extract_new_status(change):
            if pd.isnull(change):
                return None
            if '->' in change:
                parts = change.split('->')
                new_status = parts[-1].strip()
                return new_status
            else:
                return change.strip()
        
        status_df['new_status'] = status_df['new_status'].apply(extract_new_status)
        
        # Сопоставление статуса с категорией
        status_df['status_category'] = status_df['new_status'].map(status_to_category)
        
        # Обработка категории "Снято"
        removed_resolutions = ['Отклонено', 'Отменено инициатором', 'Дубликат']
        mask_removed = (status_df['status_category'] == 'Сделано') & (status_df['resolution'].isin(removed_resolutions))
        mask_removed_defects = (status_df['type'] == 'Дефект') & (status_df['new_status'] == 'Отклонен исполнителем')
        status_df.loc[mask_removed | mask_removed_defects, 'status_category'] = 'Снято'
        
        # Перевод оценки в часы
        status_df['estimation_hours'] = status_df['estimation'] / 3600
        
        # Расчет метрик
        todo_estimation = status_df[status_df['status_category'] == 'К выполнению']['estimation_hours'].sum()
        done_estimation = status_df[status_df['status_category'] == 'Сделано']['estimation_hours'].sum()
        removed_estimation = status_df[status_df['status_category'] == 'Снято']['estimation_hours'].sum()
        in_progress_estimation = status_df[status_df['status_category'] == 'В работе']['estimation_hours'].sum()
        
        # Округление значений
        todo_estimation = round(todo_estimation, 1)
        in_progress_estimation = round(in_progress_estimation, 1)
        done_estimation = round(done_estimation, 1)
        removed_estimation = round(removed_estimation, 1)
        
        # Общая оценка
        total_estimation = status_df['estimation_hours'].sum()
        
        # Расчет процентов
        todo_percentage = round((todo_estimation / total_estimation) * 100, 1) if total_estimation else 0
        removed_percentage = round((removed_estimation / total_estimation) * 100, 1) if total_estimation else 0
        
        # Вывод результатов
        print(f"К выполнению: {todo_estimation} ч ({todo_percentage}%)")
        print(f"В работе: {in_progress_estimation} ч")
        print(f"Сделано: {done_estimation} ч")
        print(f"Снято: {removed_estimation} ч ({removed_percentage}%)")
        
        # Сохранение метрик
        daily_metrics.append({
            'Дата': current_date,
            'К выполнению': todo_estimation,
            'В работе': in_progress_estimation,
            'Сделано': done_estimation,
            'Снято': removed_estimation,
            'Всего': total_estimation,
            '% К выполнению': todo_percentage,
            '% Снято': removed_percentage
        })
    
    # Преобразование списка метрик в DataFrame
    daily_metrics_df = pd.DataFrame(daily_metrics)
    print("\nЕжедневные показатели:")
    print(daily_metrics_df)
