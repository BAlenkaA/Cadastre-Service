# CadastralService
### CadastralService - сервис, который принимает запрос с указанием кадастрового номера, широты и долготы, эмулирует отправку запроса на внешний сервер, который может обрабатывать запрос до 60 секунд. Затем отдавает результат запроса. Считается, что внешний сервер может ответить `true` или `false`.
### Данные запроса на сервер и ответ с внешнего сервера сохраняются в БД. Реализовано АПИ для получения истории всех запросов/истории по кадастровому номеру.
### Стек:
* FastAPI (async роуты)
* PostgreSQL
* SQLAlchemy (async запросы)
* Alembic
* Docker
* Docker Compose
* Pytest
* fastapi-users
### Сервис содержит следующие эндпоинты:
* "/query" - принимает кадастровый номер
* "/ping" - проверка, что  сервер запустился
* "/history" - для получения истории запросов
* "/result" - эндпоинт эмулируемоего сервера, который возвращает `true` или `false`
### Для развертывания сервиса необходимо:
1. Склонировать проект git clone github.com:ваш-аккаунт-на-гитхабе/Cadastre-Service.git
2. В корне проекта создайте файл .env и заполните его. Например:
```
TITLE=Сервис эмуляции работы с кадастровым номером
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=cadastr
DB_PORT=5432
DB_HOST=db
```
3. Запускаем проект в докере командой:
```docker compose up -d```
4. Для создания первого суперюзера необходимо подключиться к базе данных через менеджер БД (например, через DBeaver) и вручную изменить значение столбца is_superuser для конкретного пользователя.