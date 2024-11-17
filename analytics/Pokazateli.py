import pandas as pd
import numpy as np
from datetime import timedelta
import ast

# Шаг 1: Загрузка данных и предварительная обработка
# Загрузка данных из CSV файлов
data = pd.read_csv('C:/Users/denis/OneDrive/Рабочий стол/T1_hack/t1_hackathon/analytics/data_for_spb_hakaton_entities1-Table_1.csv', sep=';', low_memory=False)
history = pd.read_csv('C:/Users/denis/OneDrive/Рабочий стол/T1_hack/t1_hackathon/analytics/history-Table_1.csv', sep=';', low_memory=False)
sprints = pd.read_csv('C:/Users/denis/OneDrive/Рабочий стол/T1_hack/t1_hackathon/analytics/sprints-Table_1.csv', sep=';', low_memory=False)

# Преобразование дат в формат datetime
data['create_date'] = pd.to_datetime(data['create_date'], errors='coerce')
data['update_date'] = pd.to_datetime(data['update_date'], errors='coerce')
history['history_date'] = pd.to_datetime(history['history_date'], errors='coerce')
sprints['sprint_start_date'] = pd.to_datetime(sprints['sprint_start_date'], errors='coerce')
sprints['sprint_end_date'] = pd.to_datetime(sprints['sprint_end_date'], errors='coerce')

# Преобразование entity_ids из строки в список
def parse_entity_ids(x):
    try:
        return ast.literal_eval(x)
    except:
        return []

sprints['entity_ids'] = sprints['entity_ids'].apply(parse_entity_ids)

# Конвертация оценки из секунд в часы и заполнение NaN значениями 0
data['estimation_hours'] = data['estimation'] / 3600
data['estimation_hours'] = data['estimation_hours'].fillna(0)

# Подготовка изменений статусов из истории
status_changes = history[history['history_property_name'] == 'Статус'].copy()
status_changes['history_date'] = pd.to_datetime(status_changes['history_date'], errors='coerce')

# Функция для получения нового статуса из history_change
def get_new_status(change_str):
    try:
        if pd.isnull(change_str):
            return None
        parts = change_str.split('->')
        if len(parts) > 1:
            return parts[-1].strip()
        else:
            return parts[0].strip()
    except:
        return None

status_changes['new_status'] = status_changes['history_change'].apply(get_new_status)

# Подготовка изменений резолюций из истории
resolution_changes = history[history['history_property_name'] == 'Резолюция'].copy()
resolution_changes['history_date'] = pd.to_datetime(resolution_changes['history_date'], errors='coerce')
resolution_changes['new_resolution'] = resolution_changes['history_change'].apply(get_new_status)

# Подготовка изменений спринтов из истории
sprint_changes = history[history['history_property_name'] == 'Спринт'].copy()
sprint_changes['history_date'] = pd.to_datetime(sprint_changes['history_date'], errors='coerce')
sprint_changes['sprint_change'] = sprint_changes['history_change'].apply(get_new_status)

# Подготовка связей задач (для "Заблокировано задач")
# Поскольку у нас нет данных о связях задач в предоставленных файлах, пропускаем этот шаг

# Шаг 2: Обработка каждого спринта
sprint_results = []

for idx, sprint in sprints.iterrows():
    sprint_name = sprint['sprint_name']
    sprint_start = sprint['sprint_start_date']
    sprint_end = sprint['sprint_end_date']
    entity_ids = sprint['entity_ids']
    print(f'Processing sprint: {sprint_name}')

    # Создание диапазона дат для спринта
    date_range = pd.date_range(sprint_start, sprint_end, freq='D')

    # Получение задач, связанных со спринтом
    sprint_tasks = data[data['entity_id'].isin(entity_ids)].copy()

    # Изменения статусов и резолюций для задач в спринте
    task_status_changes = status_changes[status_changes['entity_id'].isin(sprint_tasks['entity_id'])].copy()
    task_status_changes = task_status_changes.sort_values(['entity_id', 'history_date'])
    task_resolution_changes = resolution_changes[resolution_changes['entity_id'].isin(sprint_tasks['entity_id'])].copy()
    task_resolution_changes = task_resolution_changes.sort_values(['entity_id', 'history_date'])

    # Изменения спринтов для задач
    task_sprint_changes = sprint_changes[sprint_changes['entity_id'].isin(sprint_tasks['entity_id'])].copy()
    task_sprint_changes = task_sprint_changes.sort_values(['entity_id', 'history_date'])

    # Словарь для отслеживания последнего состояния спринта задачи
    last_sprint_status = {}

    # Список для хранения ежедневных данных задач
    task_dates = []

    # Обработка каждой задачи
    for task_id in sprint_tasks['entity_id'].unique():
        task_data = sprint_tasks[sprint_tasks['entity_id'] == task_id].iloc[0]

        # История изменений задачи
        task_history = task_status_changes[task_status_changes['entity_id'] == task_id]
        task_res_history = task_resolution_changes[task_resolution_changes['entity_id'] == task_id]
        task_sprint_history = task_sprint_changes[task_sprint_changes['entity_id'] == task_id]

        # Определяем начальный статус и резолюцию перед спринтом
        initial_status = task_data['status']
        initial_resolution = task_data['resolution']
        in_sprint = True  # Предполагаем, что задача в спринте, если история не говорит обратного

        pre_sprint_status = task_history[task_history['history_date'] < sprint_start]
        if not pre_sprint_status.empty:
            initial_status = pre_sprint_status.iloc[-1]['new_status']

        pre_sprint_resolution = task_res_history[task_res_history['history_date'] < sprint_start]
        if not pre_sprint_resolution.empty:
            initial_resolution = pre_sprint_resolution.iloc[-1]['new_resolution']

        # Определяем, была ли задача добавлена в спринт после его начала
        task_sprint_additions = task_sprint_history[task_sprint_history['sprint_change'] == sprint_name]
        if not task_sprint_additions.empty:
            first_addition_date = task_sprint_additions.iloc[0]['history_date']
            if first_addition_date > sprint_start:
                in_sprint = False  # Задача была добавлена после начала спринта
        else:
            # Если нет изменений спринта, проверяем дату создания задачи
            if task_data['create_date'] > sprint_start:
                in_sprint = False  # Задача создана после начала спринта

        # Построение временной шкалы изменений
        status_timeline = [{'date': sprint_start - pd.Timedelta(days=1), 'status': initial_status,
                            'resolution': initial_resolution, 'in_sprint': in_sprint}]
        combined_changes = pd.concat([
            task_history[['history_date', 'new_status']].rename(columns={'new_status': 'change', 'history_date': 'date'}),
            task_res_history[['history_date', 'new_resolution']].rename(columns={'new_resolution': 'change', 'history_date': 'date'}),
            task_sprint_history[['history_date', 'sprint_change']].rename(columns={'sprint_change': 'change', 'history_date': 'date'})
        ]).sort_values('date')

        current_status = initial_status
        current_resolution = initial_resolution
        current_in_sprint = in_sprint

        for _, row in combined_changes.iterrows():
            change_date = row['date']
            change = row['change']
            if change in ['Создано', 'В работе', 'Закрыто', 'Выполнено', 'Отклонен исполнителем']:
                current_status = change
            elif change in ['Готово', 'Отклонено', 'Отменено инициатором', 'Дубликат']:
                current_resolution = change
            else:
                # Изменение спринта
                if change == sprint_name:
                    current_in_sprint = True
                else:
                    current_in_sprint = False
            status_timeline.append({'date': change_date, 'status': current_status,
                                    'resolution': current_resolution, 'in_sprint': current_in_sprint})

        # Присваиваем статус для каждого дня
        for current_date in date_range:
            statuses_up_to_date = [item for item in status_timeline if item['date'] <= current_date]
            if not statuses_up_to_date:
                continue
            status_info = statuses_up_to_date[-1]
            status = status_info['status']
            resolution = status_info['resolution']
            in_sprint = status_info['in_sprint']

            task_dates.append({
                'date': current_date,
                'entity_id': task_id,
                'status': status,
                'resolution': resolution,
                'type': task_data['type'],
                'estimation_hours': task_data['estimation_hours'],
                'in_sprint': in_sprint
            })

    # Создаем DataFrame с ежедневными статусами задач
    task_status_per_day = pd.DataFrame(task_dates)

    # Фильтруем задачи, которые в спринте в текущий день
    task_status_per_day = task_status_per_day[task_status_per_day['in_sprint']]

    # Функция для отображения статуса в категорию
    def map_status_category(status, resolution, task_type):
        if status == 'Создано':
            return 'К выполнению'
        elif status == 'В работе':
            return 'В работе'
        elif status in ['Закрыто', 'Выполнено']:
            if resolution in ['Отклонено', 'Отменено инициатором', 'Дубликат']:
                return 'Снято'
            else:
                return 'Сделано'
        elif task_type == 'Дефект' and status == 'Отклонен исполнителем':
            return 'Снято'
        else:
            return 'В работе'

    # Применяем функцию к каждой строке
    task_status_per_day['status_category'] = task_status_per_day.apply(
        lambda row: map_status_category(row['status'], row['resolution'], row['type']), axis=1
    )

    # Определяем 'Снятые объекты'
    task_status_per_day['is_snyato'] = task_status_per_day['status_category'] == 'Снято'

    # Ежедневные суммы по категориям
    daily_sums = task_status_per_day.groupby(['date', 'status_category'])['estimation_hours'].sum().reset_index()
    daily_indicators = daily_sums.pivot(index='date', columns='status_category', values='estimation_hours').fillna(0).reset_index()

    # Убедимся, что все необходимые колонки присутствуют
    for col in ['К выполнению', 'В работе', 'Сделано', 'Снято']:
        if col not in daily_indicators.columns:
            daily_indicators[col] = 0

    # Расчет "Бэклог изменен с начала спринта на"
    sprint_task_ids = sprint_tasks['entity_id'].unique()
    task_added_dates = {}

    # Обработка изменений спринта для задач
    task_sprint_changes = sprint_changes[sprint_changes['entity_id'].isin(sprint_task_ids)]
    task_sprint_changes = task_sprint_changes.sort_values(['entity_id', 'history_date'])

    for task_id in sprint_task_ids:
        task_changes = task_sprint_changes[task_sprint_changes['entity_id'] == task_id]
        task_changes_in_sprint = task_changes[task_changes['sprint_change'] == sprint_name]
        if not task_changes_in_sprint.empty:
            added_date = task_changes_in_sprint.iloc[0]['history_date']
        else:
            # Если задача была в спринте с самого начала
            added_date = sprint_start - pd.Timedelta(days=1)
        task_added_dates[task_id] = added_date

    cutoff_date = sprint_start + timedelta(days=2)
    early_tasks = [task_id for task_id, date in task_added_dates.items() if date <= cutoff_date]
    late_tasks = [task_id for task_id, date in task_added_dates.items() if date > cutoff_date]

    # Исключаем дефекты
    early_tasks_df = sprint_tasks[(sprint_tasks['entity_id'].isin(early_tasks)) & (sprint_tasks['type'] != 'Дефект')]
    late_tasks_df = sprint_tasks[(sprint_tasks['entity_id'].isin(late_tasks)) & (sprint_tasks['type'] != 'Дефект')]

    early_sum = early_tasks_df['estimation_hours'].sum()
    late_sum = late_tasks_df['estimation_hours'].sum()

    # Исправление расчета для случаев, когда early_sum == 0
    if early_sum > 0:
        backlog_change_pct = (late_sum * 100) / early_sum
    elif late_sum > 0:
        backlog_change_pct = 100.0  # Весь бэклог был добавлен поздно
    else:
        backlog_change_pct = 0.0  # Нет задач в бэклоге

    # Округляем до одного знака после запятой
    backlog_change_pct = round(backlog_change_pct, 1)

    # Добавляем "Бэклог изменен с начала спринта на" в ежедневные показатели
    daily_indicators['Бэклог изменен с начала спринта на'] = backlog_change_pct

    # Добавляем название спринта
    daily_indicators['sprint_name'] = sprint_name

    # Расчет "Добавлено (ЧД/шт)" и "Исключено (ЧД/шт)"
    daily_added = []
    daily_removed = []

    for current_date in date_range:
        task_daily_changes = {}
        # Фильтруем изменения спринта на текущую дату
        task_changes_on_date = task_sprint_changes[task_sprint_changes['history_date'].dt.date == current_date.date()]
        for _, row in task_changes_on_date.iterrows():
            task_id = row['entity_id']
            change = row['sprint_change']
            # Обновляем последнее изменение задачи в словаре
            task_daily_changes[task_id] = change

        added_tasks = []
        removed_tasks = []

        # Определяем добавленные и исключенные задачи на текущий день
        for task_id, change in task_daily_changes.items():
            is_snyato = task_status_per_day[
                (task_status_per_day['date'] == current_date) &
                (task_status_per_day['entity_id'] == task_id)
            ]['is_snyato'].any()
            if not is_snyato:
                if change == sprint_name:
                    added_tasks.append(task_id)
                else:
                    removed_tasks.append(task_id)

        # Суммируем оценки и количество
        added_estimation = sprint_tasks[sprint_tasks['entity_id'].isin(added_tasks)]['estimation_hours'].sum()
        added_count = len(added_tasks)
        removed_estimation = sprint_tasks[sprint_tasks['entity_id'].isin(removed_tasks)]['estimation_hours'].sum()
        removed_count = len(removed_tasks)

        daily_added.append({'date': current_date, 'Добавлено_Часы': added_estimation, 'Добавлено_Количество': added_count})
        daily_removed.append({'date': current_date, 'Исключено_Часы': removed_estimation, 'Исключено_Количество': removed_count})

    # Преобразуем в DataFrame
    daily_added_df = pd.DataFrame(daily_added)
    daily_removed_df = pd.DataFrame(daily_removed)

    # Объединяем с ежедневными показателями
    daily_indicators = daily_indicators.merge(daily_added_df, on='date', how='left')
    daily_indicators = daily_indicators.merge(daily_removed_df, on='date', how='left')

    # Заполняем NaN нулями
    daily_indicators[['Добавлено_Часы', 'Добавлено_Количество', 'Исключено_Часы', 'Исключено_Количество']] = daily_indicators[['Добавлено_Часы', 'Добавлено_Количество', 'Исключено_Часы', 'Исключено_Количество']].fillna(0)

    # Добавляем результаты спринта в общий список
    sprint_results.append(daily_indicators)

# Объединяем результаты всех спринтов
final_results = pd.concat(sprint_results, ignore_index=True)

# output_path = 'D:/final_results.csv'
# final_results.to_csv(output_path, index=False, encoding='utf-8-sig')

# Выводим результаты
print(final_results.head(30))
print(final_results['Бэклог изменен с начала спринта на'])
