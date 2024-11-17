# Базовый образ
FROM python:3.9-slim

# Рабочая директория
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта
COPY . /app

# Запуск
CMD ["python", "main.py"]
