from fastapi import FastAPI
from routers import predict, train, update

app = FastAPI()

# Подключение маршрутов
app.include_router(predict.router)
app.include_router(train.router)
app.include_router(update.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Clustering Service"}
