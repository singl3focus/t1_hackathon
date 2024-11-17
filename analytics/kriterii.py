import pandas as pd
import numpy as np

df= pd.read_csv ('D:/final_results.csv')
df_needs= df[['sprint_name', 'date','К выполнению', 'В работе',  'Сделано', 'Снято', 'Бэклог изменен с начала спринта на']]
print (df_needs)

#output_path = 'D:/df_needs.csv'
#df_needs.to_csv(output_path, index=False, encoding='utf-8-sig')

import pandas as pd

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

    # 1. Проверка равномерности изменения статусов
    last_day = sprint_data['date'].max()
    last_day_data = sprint_data[sprint_data['date'] == last_day]
    if (last_day_data['Сделано'] > last_day_data['Сделано'].mean() * 1.5).any():
        violations.append("Массовый переход задач в статус 'Сделано' в последний день")

    # 2. Проверка параметра "К выполнению" (не более 20% от общего объема)
    sprint_data['К выполнению доля'] = sprint_data['К выполнению'] / (
        sprint_data[['К выполнению', 'В работе', 'Сделано', 'Снято']].sum(axis=1)
    )
    if (sprint_data['К выполнению доля'] > 0.2).any():
        violations.append("Параметр 'К выполнению' превышает 20% от общего объема")

    # 3. Проверка параметра "Снято" (не более 10% от общего объема)
    sprint_data['Снято доля'] = sprint_data['Снято'] / (
        sprint_data[['К выполнению', 'В работе', 'Сделано', 'Снято']].sum(axis=1)
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

for sprint_name in df_needs['sprint_name'].unique():
    status, issues = evaluate_sprint_success(df_needs, sprint_name)
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

#output_path = 'D:/df_needs.csv'
#df_needs.to_csv(output_path, index=False, encoding='utf-8-sig')
