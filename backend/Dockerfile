FROM golang:1.21.6-bullseye

WORKDIR /backend

COPY . ./

# Установка зависимостей проекта
RUN go mod download

# Сборка проекта
RUN go build -o ./bin/api ./cmd/app/main.go

EXPOSE 5001

# Команда для запуска контейнера
CMD ["./bin/api"]