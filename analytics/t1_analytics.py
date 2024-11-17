import pandas as pd

# Загрузка данных
data = pd.read_csv('data_for_spb_hakaton_entities1-Table 1.csv', sep=';')
history = pd.read_csv('history-Table 1.csv', sep=';', index_col=None)
sprints = pd.read_csv('sprints-Table 1.csv', sep=';', index_col=None)

# Сдвиг колонок влево, чтобы "entity_id" стало первой колонкой
history = history.reset_index()  # Сброс индекса
columns = history.columns.tolist()  # Получаем текущий список колонок
columns = columns[1:] + columns[:1]  # Перемещаем первую колонку в конец
history.columns = columns  # Переупорядочиваем названия колонок
if 'index' in history.columns:
    history.drop(columns=['index'], inplace=True)

# Разделение entity_ids в таблице sprints
sprints['entity_ids'] = sprints['entity_ids'].apply(lambda x: x.strip('{}').split(',') if pd.notnull(x) else [])
sprints_expanded = sprints.explode('entity_ids')
sprints_expanded['entity_id'] = sprints_expanded['entity_ids'].astype(float)

# Удаляем строки с некорректным типом в entity_id из history
history = history[history['entity_id'].apply(lambda x: isinstance(x, (int, float)))]

# Приведение entity_id в обоих таблицах к одному типу (float)
data['entity_id'] = data['entity_id'].astype(float)
history['entity_id'] = history['entity_id'].astype(float)

# Соединение data и sprints
data_sprints = pd.merge(data, sprints_expanded, on='entity_id', how='left')

# Соединение data_sprints с history
final_table = pd.merge(data_sprints, history, on='entity_id', how='left')

# Просмотр результата
print(final_table.head())

# Если требуется сохранение в файл
final_table.to_csv('merged_data.csv', index=False)

data = final_table.copy()


# Условия для фильтрации задач
valid_statuses = ["Закрыто", "Выполнено"]
valid_resolutions = ["Отклонено", "Отменено инициатором", "Дубликат", "Отклонён исполнителем"]

# Инициализация метрик
daily_metrics = []

# Преобразование дат в DataFrame
data['history_date'] = pd.to_datetime(data['history_date'], errors='coerce')

# Получение уникальных спринтов
unique_sprints = data['sprint_name'].unique()

# Цикл по каждому спринту
for sprint_name in unique_sprints:
    # Фильтрация данных по текущему спринту
    sprint_data = data[data['sprint_name'] == sprint_name]

    # Определение диапазона дат спринта
    sprint_start_date = sprint_data['history_date'].min()
    sprint_end_date = sprint_data['history_date'].max()

    # Проход по дням спринта
    current_date = sprint_start_date
    while current_date <= sprint_end_date:
        # Фильтрация задач, относящихся к текущему дню и удовлетворяющих условиям
        tasks_cancelled_on_day = sprint_data[
            (sprint_data['status'].isin(valid_statuses)) &
            (sprint_data['resolution'].isin(valid_resolutions)) &
            (sprint_data['history_date'] <= current_date)
        ]

        # Суммирование estimation и деление на 3600
        daily_metric = tasks_cancelled_on_day['estimation'].sum() / 3600

        # Добавление метрики в список
        daily_metrics.append({
            'sprint_name': sprint_name,
            'date': current_date,
            'second_metric': round(daily_metric, 1)
        })

        # Переход к следующему дню
        current_date += pd.Timedelta(days=1)

# Создание DataFrame с ежедневными метриками
daily_metrics_df = pd.DataFrame(daily_metrics)


# Выбор конкретного спринта
selected_sprint_entity_ids = sprints.iloc[0]['entity_ids']  # Уже является списком

# Фильтрация задач, относящихся к выбранному спринту, со статусом "Создано"
tasks_in_sprint = data[
    (data['entity_id'].isin(selected_sprint_entity_ids)) &
    (data['status'] == 'Создано')
]

# Суммирование estimation и деление на 3600
first_metric_sum = tasks_in_sprint['estimation'].sum() / 3600  # Перевод в часы

# Создание отдельного столбца с рассчитанным показателем для каждой строки (если нужен общий результат - только sum)
data['first_metric'] = 0  # Инициализация
data.loc[
    data['entity_id'].isin(selected_sprint_entity_ids),
    'first_metric'
] = first_metric_sum


# Группируем задачи по sprintName и рассчитываем метрику "К выполнению"
def calculate_metric_per_sprint(df, sprint_name):
    # Фильтрация задач, относящихся к указанному спринту и имеющих статус "Создано"
    tasks_in_sprint = df[
        (df['sprint_name'] == sprint_name) &
        (df['status'] == 'Создано')
    ]
    # Суммирование estimation для задач спринта и деление на 3600
    metric = tasks_in_sprint['estimation'].sum() / 3600
    return metric

# Применяем расчёт метрики по каждому уникальному спринту
sprint_metrics = {}
for sprint_name in data['sprint_name'].unique():
    sprint_metrics[sprint_name] = calculate_metric_per_sprint(data, sprint_name)

# Добавляем результат в таблицу
daily_metrics_df['first_metrick'] = data['sprint_name'].map(sprint_metrics)



# Преобразуем столбец sprint_start_date и sprint_end_date в datetime
sprints['sprint_start_date'] = pd.to_datetime(sprints['sprint_start_date'], errors='coerce')
sprints['sprint_end_date'] = pd.to_datetime(sprints['sprint_end_date'], errors='coerce')

# Функция для разделения задач по времени относительно дня спринта
def split_tasks_by_day(df, current_date):
    # Преобразуем history_date в datetime
    df['history_date'] = pd.to_datetime(df['history_date'], errors='coerce')
    
    # Задачи до текущей даты
    early_tasks_df = df[
        (df['history_date'].isna() | (df['history_date'] <= current_date)) &
        (df['type'] != 'Дефект')  # Исключаем дефекты
    ]
    
    # Задачи, добавленные до текущей даты
    added_tasks_df = df[
        (df['history_date'] > current_date) &
        (df['type'] != 'Дефект')  # Исключаем дефекты
    ]
    
    return early_tasks_df, added_tasks_df

# Функция для подсчета backlog_change для определённого дня спринта
def calculate_daily_backlog_change(data, sprint, current_date):
    # Разделяем задачи на те, что существовали до текущей даты, и те, что добавились
    early_tasks_df, added_tasks_df = split_tasks_by_day(data, current_date)

    # Считаем сумму оценок
    early_sum = early_tasks_df['estimation'].sum() / 3600  # Переводим секунды в часы
    added_sum = added_tasks_df['estimation'].sum() / 3600  # Переводим секунды в часы

    # Исправление расчета для случаев, когда early_sum == 0
    if early_sum > 0:
        backlog_change_pct = (added_sum * 100) / early_sum
    elif added_sum > 0:
        backlog_change_pct = 100.0  # Весь бэклог был добавлен поздно
    else:
        backlog_change_pct = 0.0  # Нет задач в бэклоге

    return round(backlog_change_pct, 1)

# Рассчитываем backlog_change для каждого дня в каждом спринте
daily_backlog_metrics = []
for _, sprint in sprints.iterrows():
    sprint_name = sprint['sprint_name']
    sprint_start_date = sprint['sprint_start_date']
    sprint_end_date = sprint['sprint_end_date']
    
    # Перебор дней спринта
    current_date = sprint_start_date
    while current_date <= sprint_end_date:
        backlog_change_pct = calculate_daily_backlog_change(data, sprint, current_date)
        daily_backlog_metrics.append({
            'sprint_name': sprint_name,
            'day': current_date,
            'backlog_change_percentage': backlog_change_pct
        })
        current_date += pd.Timedelta(days=1)  # Переходим к следующему дню

# Создаем итоговый DataFrame с ежедневными метриками
daily_backlog_metrics_df = pd.DataFrame(daily_backlog_metrics)


merged_df = pd.merge(
    daily_backlog_metrics_df,
    daily_metrics_df,
    on="sprint_name",        # Замените "date" на ваш общий столбец
    how="right"       # Тип соединения: 'inner', 'left', 'right', 'outer'
)

# Отобразим результат
print(merged_df.head(5))

#first metric- к выполнению 
#second_metric- снято


merged_df.rename (columns= {'first_metrick': "К выполнению", 'second_metric':"Снято"}, inplace = True)

daily_backlog_metrics_df['day'] = pd.to_datetime(daily_backlog_metrics_df['day']).dt.date

# Удаление времени из столбца "date" в daily_metrics_df
daily_metrics_df['date'] = pd.to_datetime(daily_metrics_df['date']).dt.date

# Переименование столбца "date" в daily_metrics_df для слияния
daily_metrics_df.rename(columns={'date': 'day'}, inplace=True)

# Мерджинг двух датафреймов по "sprint_name" и "day"
merged_df = pd.merge(
    daily_backlog_metrics_df,
    daily_metrics_df,
    on=['sprint_name', 'day'],
    how='inner'
)

merged_df.rename(columns= {'first_metrick':"К выполнению", 'second_metric':"Снято", 'backlog_change_percentage': "Бэклог изменен с начала спринта на"}, inplace= True)



def evaluate_sprint_success(df, sprint_name):
    """
    Оценивает успешность спринта по заданным критериям.

    :param df: DataFrame с данными о спринтах
    :param sprint_name: Название спринта для анализа
    :return: "Успешный" или "Неуспешный" и описание нарушенных критериев
    """
    # Фильтрация данных по названию спринта
    sprint_data = df[df['sprint_name'] == sprint_name].copy()

    # Проверка на пустой спринт
    if sprint_data.empty:
        return "Неуспешный", f"Спринт с названием '{sprint_name}' отсутствует в данных"

    # Критерии успешности
    violations = []


    # 2. Проверка параметра "К выполнению" (не более 20% от общего объема)
    sprint_data['К выполнению доля'] = sprint_data['К выполнению'] / (
        sprint_data[['К выполнению', 'Снято']].sum(axis=1)
    )
    if (sprint_data['К выполнению доля'] > 0.2).any():
        violations.append("Параметр 'К выполнению' превышает 20% от общего объема")

    # 3. Проверка параметра "Снято" (не более 10% от общего объема)
    sprint_data['Снято доля'] = sprint_data['Снято'] / (
        sprint_data[['К выполнению', 'Снято']].sum(axis=1)
    )
    if (sprint_data['Снято доля'] > 0.1).any():
        violations.append("Параметр 'Снято' превышает 10% от общего объема")

    # 4. Проверка изменения бэклога (не более 20%)
    if (sprint_data['Бэклог изменен с начала спринта на'] > 20).any():
        violations.append("Бэклог изменен более чем на 20% после начала спринта")

    # Результат
    if violations:
        return "Неуспешный", violations
    else:
        return "Успешный", []


sprint_status = {}

for sprint_name in merged_df['sprint_name'].unique():
    status, issues = evaluate_sprint_success(merged_df, sprint_name)
    sprint_status[sprint_name] = {
        "Статус": status,
        "Нарушения": issues
    }

# Вывод результата
for sprint, result in sprint_status.items():
    print(f"Спринт: {sprint}")
    print(f"Статус: {result['Статус']}")
    if result['Нарушения']:
        print(f"Нарушения: {', '.join(result['Нарушения'])}")
    print("-" * 50)
