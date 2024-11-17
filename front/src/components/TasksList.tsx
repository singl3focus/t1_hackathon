import { useState, useEffect } from 'react';
import axios from 'axios';

// Типы данных для задач, соответствующие структуре Go
interface TaskTypes {
  entity_id: number;
  area: string;
  type: string;
  status: string;
  state: string;
  priority: string;
  ticket_number: string;
  name: string;
  create_date: string; // Будет строкой (формат даты)
  created_by: string;
  update_date: string; // Будет строкой (формат даты)
  updated_by: string;
  parent_ticket_id: number | null; // Может быть null
  assignee: string | null; // Может быть null
  owner: string;
  due_date: string | null; // Может быть null
  rank: string;
  estimation: number | null; // Может быть null
  spent: number | null; // Может быть null
  resolution: string | null; // Может быть null
}

interface TaskListProps {
  sprintId: number; // ID спринта, для которого нужно получить задачи
}

const TaskList: React.FC<TaskListProps> = ({ sprintId }) => {
  const [tasks, setTasks] = useState<TaskTypes[]>([]); // Состояние для списка задач
  const [loading, setLoading] = useState<boolean>(true); // Состояние загрузки
  const [error, setError] = useState<string>(''); // Сообщение об ошибке, если что-то пошло не так

  // Функция для получения задач
  const fetchTasks = async () => {
    try {
      const response = await axios.get(`/sprint/task/all?sprint_id=${sprintId}`);
      setTasks(response.data);
    } catch (err) {
      setError('Error fetching tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks(); // Запрос задач при монтировании компонента
  }, [sprintId]); // Перезапуск запроса, если меняется ID спринта

  // Форматирование даты для вывода
  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return 'N/A'; // Если дата пустая, выводим 'N/A'
    const date = new Date(dateStr);
    return date.toLocaleDateString(); // Преобразуем в строку формата "день/месяц/год"
  };

  // Рендеринг состояния компонента
  if (loading) {
    return <div>Loading tasks...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      <h2>Tasks for Sprint {sprintId}</h2>
      <ul>
        {tasks.map((task) => (
          <li key={task.entity_id}>
            <div>
              <strong>{task.name}</strong>
            </div>
            <div>Assignee: {task.assignee ?? 'N/A'}</div> {/* Если assignee null, выводим 'N/A' */}
            <div>Status: {task.status}</div>
            <div>Due Date: {formatDate(task.due_date)}</div>
            <div>Priority: {task.priority}</div>
            <div>Created By: {task.created_by}</div>
            <div>Owner: {task.owner}</div>
            <div>Resolution: {task.resolution ?? 'N/A'}</div> {/* Если resolution null, выводим 'N/A' */}
            <div>Estimation: {task.estimation !== null ? task.estimation : 'N/A'}</div> {/* Если estimation null, выводим 'N/A' */}
            <div>Spent: {task.spent !== null ? task.spent : 'N/A'}</div> {/* Если spent null, выводим 'N/A' */}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TaskList;
