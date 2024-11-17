from fastapi import FastAPI
from routers import predict, train, update
import os

app = FastAPI(
    title="Clustering Service API",
    description="API for clustering data, training, and updating models.",
    version="1.0.0"
)

# Проверка наличия необходимых файлов или создание заглушек
def initialize_model_files():
    placeholder_file = "trained_model.json"
    if not os.path.exists(placeholder_file):
        with open(placeholder_file, "w") as file:
            file.write("{}")  # Создаем пустой JSON для сохранения модели

# Инициализация модели при старте сервиса
@app.on_event("startup")
def startup_event():
    initialize_model_files()

# Подключение маршрутов
app.include_router(predict.router)
app.include_router(train.router)
app.include_router(update.router)

@app.get("/")
def read_root():
    """
    Корневой маршрут для проверки работоспособности API.
    """
    return {"message": "Welcome to the Clustering Service API!"}



if __name__ == '__main__':
    app.run()