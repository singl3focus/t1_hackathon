import pandas as pd
import numpy as np
from datetime import timedelta
import ast

# Шаг 1: Загрузка данных и предварительная обработка
# Загрузка данных из CSV
data = pd.read_csv('C:/Users/Alexe/OneDrive/Рабочий стол/data_for_spb_hakaton_entities1-Table 1.csv', sep=';', low_memory=False)
history = pd.read_csv('C:/Users/Alexe/OneDrive/Рабочий стол/history-Table 1.csv', sep=';', low_memory=False)
sprints = pd.read_csv('C:/Users/Alexe/OneDrive/Рабочий стол/sprints-Table 1.csv', sep=';', low_memory=False)

data['create_date'] = pd.to_datetime(data['create_date'], errors='coerce')
data['update_date'] = pd.to_datetime(data['update_date'], errors='coerce')
history['history_date'] = pd.to_datetime(history['history_date'], errors='coerce')
sprints['sprint_start_date'] = pd.to_datetime(sprints['sprint_start_date'], errors='coerce')
sprints['sprint_end_date'] = pd.to_datetime(sprints['sprint_end_date'], errors='coerce')

# Convert entity_ids to list
def parse_entity_ids(x):
    try:
        return ast.literal_eval(x)
    except:
        return []

sprints['entity_ids'] = sprints['entity_ids'].apply(parse_entity_ids)

# Convert estimates from seconds to hours
data['estimation_hours'] = data['estimation'] / 3600
data['estimation_hours'] = data['estimation_hours'].fillna(0)

# Prepare status changes from history
status_changes = history[history['history_property_name'] == 'Статус'].copy()

# Parse history_change to get the new status
def get_new_status(change_str):
    try:
        if pd.isnull(change_str):
            return None
        return change_str.split('->')[-1].strip()
    except:
        return None

status_changes['new_status'] = status_changes['history_change'].apply(get_new_status)

# Prepare resolution changes from history
resolution_changes = history[history['history_property_name'] == 'Резолюция'].copy()
resolution_changes['new_resolution'] = resolution_changes['history_change'].apply(get_new_status)

# Prepare sprint changes from history
sprint_changes = history[history['history_property_name'] == 'Спринт'].copy()
sprint_changes['sprint_added'] = sprint_changes['history_change'].apply(lambda x: get_new_status(x))

# Process each sprint
sprint_results = []

for idx, sprint in sprints.iterrows():
    sprint_name = sprint['sprint_name']
    sprint_start = sprint['sprint_start_date']
    sprint_end = sprint['sprint_end_date']
    entity_ids = sprint['entity_ids']
    print(f'Processing sprint: {sprint_name}')

    date_range = pd.date_range(sprint_start, sprint_end)

    sprint_tasks = data[data['entity_id'].isin(entity_ids)].copy()

    # Get status and resolution changes for tasks in the sprint
    task_status_changes = status_changes[status_changes['entity_id'].isin(sprint_tasks['entity_id'])].copy()
    task_status_changes.sort_values(['entity_id', 'history_date'], inplace=True)
    task_resolution_changes = resolution_changes[resolution_changes['entity_id'].isin(sprint_tasks['entity_id'])].copy()
    task_resolution_changes.sort_values(['entity_id', 'history_date'], inplace=True)

    # Get sprint changes for tasks
    task_sprint_changes = sprint_changes[sprint_changes['entity_id'].isin(sprint_tasks['entity_id'])].copy()
    task_sprint_changes.sort_values(['entity_id', 'history_date'], inplace=True)

    task_dates = []

    for task_id in sprint_tasks['entity_id'].unique():
        task_data = sprint_tasks[sprint_tasks['entity_id'] == task_id].iloc[0]

        # Get full history for the task
        task_history = task_status_changes[task_status_changes['entity_id'] == task_id]
        task_res_history = task_resolution_changes[task_resolution_changes['entity_id'] == task_id]
        task_sprint_history = task_sprint_changes[task_sprint_changes['entity_id'] == task_id]

        # Determine initial status and resolution before the sprint
        initial_status = task_data['status']
        initial_resolution = task_data['resolution']
        in_sprint = True  # Assume the task is in sprint unless history says otherwise

        pre_sprint_status = task_history[task_history['history_date'] < sprint_start]
        if not pre_sprint_status.empty:
            initial_status = pre_sprint_status.iloc[-1]['new_status']

        pre_sprint_resolution = task_res_history[task_res_history['history_date'] < sprint_start]
        if not pre_sprint_resolution.empty:
            initial_resolution = pre_sprint_resolution.iloc[-1]['new_resolution']

        # Determine if task was added to sprint after the start
        pre_sprint_sprint = task_sprint_history[task_sprint_history['history_date'] < sprint_start]
        if not pre_sprint_sprint.empty:
            last_sprint_change = pre_sprint_sprint.iloc[-1]['sprint_added']
            if last_sprint_change != sprint_name:
                in_sprint = False
        else:
            # If there is no sprint change history before sprint start, check if task was created before sprint
            if task_data['create_date'] > sprint_start:
                in_sprint = False

        # Build a timeline of status, resolution, and sprint membership changes
        status_timeline = [{'date': sprint_start - pd.Timedelta(days=1), 'status': initial_status, 'resolution': initial_resolution, 'in_sprint': in_sprint}]
        combined_changes = pd.concat([
            task_history[['history_date', 'new_status']].rename(columns={'new_status': 'change', 'history_date': 'date'}),
            task_res_history[['history_date', 'new_resolution']].rename(columns={'new_resolution': 'change', 'history_date': 'date'}),
            task_sprint_history[['history_date', 'sprint_added']].rename(columns={'sprint_added': 'change', 'history_date': 'date'})
        ]).sort_values('date')

        current_status = initial_status
        current_resolution = initial_resolution
        current_in_sprint = in_sprint

        for _, row in combined_changes.iterrows():
            change_date = row['date']
            change = row['change']
            if change in status_changes['new_status'].values:
                current_status = change
            elif change in resolution_changes['new_resolution'].values:
                current_resolution = change
            else:
                # Sprint change
                if change == sprint_name:
                    current_in_sprint = True
                else:
                    current_in_sprint = False
            status_timeline.append({'date': change_date, 'status': current_status, 'resolution': current_resolution, 'in_sprint': current_in_sprint})

        # Assign status for each day
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

    # Create DataFrame
    task_status_per_day = pd.DataFrame(task_dates)

    # Filter tasks that are in sprint on that day
    task_status_per_day = task_status_per_day[task_status_per_day['in_sprint']]

    # Map status to status_category
    def map_status_category(status, resolution, task_type):
        if status == 'Создано':
            return 'To Do'
        elif status == 'В работе':
            return 'In Progress'
        elif status in ['Закрыто', 'Выполнено']:
            if resolution in ['Отклонено', 'Отменено инициатором', 'Дубликат'] or (task_type == 'Дефект' and status == 'Отклонен исполнителем'):
                return 'Removed'
            else:
                return 'Done'
        else:
            return 'Other'

    task_status_per_day['status_category'] = task_status_per_day.apply(
        lambda row: map_status_category(row['status'], row['resolution'], row['type']), axis=1
    )

    # Identify 'Снятые объекты'
    task_status_per_day['is_snyato'] = task_status_per_day.apply(
        lambda row: row['status_category'] == 'Removed', axis=1
    )

    # Calculate daily sums
    daily_sums = task_status_per_day.groupby(['date', 'status_category'])['estimation_hours'].sum().reset_index()
    daily_indicators = daily_sums.pivot(index='date', columns='status_category', values='estimation_hours').fillna(0).reset_index()

    # Ensure all required columns are present
    for col in ['To Do', 'In Progress', 'Done', 'Removed']:
        if col not in daily_indicators.columns:
            daily_indicators[col] = 0

    # Calculate "Backlog Change %"
    sprint_task_ids = sprint_tasks['entity_id'].unique()
    task_added_dates = {}

    # Process sprint changes
    task_sprint_changes = sprint_changes[sprint_changes['entity_id'].isin(sprint_task_ids)]
    task_sprint_changes.sort_values(['entity_id', 'history_date'], inplace=True)

    for task_id in sprint_task_ids:
        task_changes = task_sprint_changes[task_sprint_changes['entity_id'] == task_id]
        task_changes_in_sprint = task_changes[task_changes['sprint_added'] == sprint_name]
        if not task_changes_in_sprint.empty:
            added_date = task_changes_in_sprint.iloc[0]['history_date']
        else:
            # If task was in sprint from the beginning
            added_date = sprint_start - pd.Timedelta(days=1)
        task_added_dates[task_id] = added_date

    cutoff_date = sprint_start + timedelta(days=2)
    early_tasks = [task_id for task_id, date in task_added_dates.items() if date <= cutoff_date]
    late_tasks = [task_id for task_id, date in task_added_dates.items() if date > cutoff_date]

    # Exclude defects
    early_tasks_df = sprint_tasks[(sprint_tasks['entity_id'].isin(early_tasks)) & (sprint_tasks['type'] != 'Дефект')]
    late_tasks_df = sprint_tasks[(sprint_tasks['entity_id'].isin(late_tasks)) & (sprint_tasks['type'] != 'Дефект')]

    early_sum = early_tasks_df['estimation_hours'].sum()
    late_sum = late_tasks_df['estimation_hours'].sum()

    if early_sum > 0:
        backlog_change_pct = (late_sum * 100) / early_sum
    else:
        backlog_change_pct = 0

    daily_indicators['Backlog Change %'] = round(backlog_change_pct, 1)
    daily_indicators['sprint_name'] = sprint_name

    # Calculate "Добавлено (ЧД/шт)" and "Исключено (ЧД/шт)"
    # Initialize lists to hold daily added and removed tasks
    daily_added = []
    daily_removed = []

    for current_date in date_range:
        # Get tasks added or removed on current_date
        added_tasks = []
        removed_tasks = []

        for task_id in sprint_task_ids:
            task_changes = task_sprint_changes[task_sprint_changes['entity_id'] == task_id]
            changes_on_date = task_changes[task_changes['history_date'].dt.date == current_date.date()]
            if not changes_on_date.empty:
                for _, row in changes_on_date.iterrows():
                    change = row['sprint_added']
                    if change == sprint_name:
                        added_tasks.append(task_id)
                    else:
                        removed_tasks.append(task_id)

        # Exclude 'Снятые' tasks
        snyato_tasks = task_status_per_day[(task_status_per_day['date'] == current_date) & (task_status_per_day['is_snyato'])]['entity_id'].unique()
        added_tasks = [tid for tid in added_tasks if tid not in snyato_tasks]
        removed_tasks = [tid for tid in removed_tasks if tid not in snyato_tasks]

        # Handle multiple additions/removals in a single day
        added_tasks = list(set(added_tasks))
        removed_tasks = list(set(removed_tasks))

        # Sum estimation hours and counts
        added_estimation = sprint_tasks[sprint_tasks['entity_id'].isin(added_tasks)]['estimation_hours'].sum()
        added_count = len(added_tasks)
        removed_estimation = sprint_tasks[sprint_tasks['entity_id'].isin(removed_tasks)]['estimation_hours'].sum()
        removed_count = len(removed_tasks)

        daily_added.append({'date': current_date, 'Added_Hours': added_estimation, 'Added_Count': added_count})
        daily_removed.append({'date': current_date, 'Removed_Hours': removed_estimation, 'Removed_Count': removed_count})

    # Convert to DataFrames
    daily_added_df = pd.DataFrame(daily_added)
    daily_removed_df = pd.DataFrame(daily_removed)

    # Merge with daily_indicators
    daily_indicators = daily_indicators.merge(daily_added_df, on='date', how='left')
    daily_indicators = daily_indicators.merge(daily_removed_df, on='date', how='left')

    # Fill NaN values with zeros
    daily_indicators[['Added_Hours', 'Added_Count', 'Removed_Hours', 'Removed_Count']] = daily_indicators[['Added_Hours', 'Added_Count', 'Removed_Hours', 'Removed_Count']].fillna(0)

    # Append results
    sprint_results.append(daily_indicators)

# Combine results for all sprints
final_results = pd.concat(sprint_results, ignore_index=True)



output_path = 'D:/final_results.csv'
final_results.to_csv(output_path, index=False, encoding='utf-8')



# Print results
print(final_results)
