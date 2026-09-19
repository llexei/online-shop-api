English version: [README.md](README.md)
# Online Shop API

REST API небольшого интернет-магазина: каталог, корзина, заказы, роли и отправка письма после оформления заказа.

Портфолио-проект по бэкенду, без фронтенда. Основной интерфейс — Swagger.

## Возможности

- Регистрация и вход по JWT
- Роли: пользователь, менеджер, админ
- Каталог товаров и категории
- Корзина
- Оформление заказа
- Статусы заказа
- Проверка остатков перед покупкой
- Redis: хранение / блеклист токенов и rate limit по IP
- Celery: письмо после создания заказа
- Mailhog для локального просмотра писем
- Логирование заказов, ошибок авторизации и задач воркера
- Интеграционные тесты ручек и задачи на письмо
- Docker Compose: API, worker, PostgreSQL, Redis, Mailhog

## Стек

- Python 3.12
- FastAPI
- SQLAlchemy + PostgreSQL
- Pydantic
- Redis
- Celery
- Mailhog
- Pytest
- Docker / Docker Compose

## Архитектура

```
client -> FastAPI
|-- PostgreSQL   (users, products, cart, orders)
|-- Redis        (tokens / rate limit / Celery broker)
`-- Celery worker -> Mailhog
```

Бизнес-логика живёт в сервисах, а не в ручках:

- нельзя купить больше, чем есть на складе
- после успешного заказа остаток уменьшается
- статус заказа меняется только по разрешённым переходам
- админские и менеджерские ручки закрыты проверкой роли, обычный пользователь не может ими пользоваться
- письмо не отправляется внутри запроса: API выводит задачу фоном, ставит ее в Celery

## Структура проекта
```bash
app/
├──api/           # роуты
├──core/          # бд, конфиг, безопасность, логирование, rate limit, celery app
├──models/        # SQLAlchemy модели
├──schemas/       # Pydantic-схемы
├──services/      # бизнес-логика роутов
├──tasks/         # задачи Celery
tests/            # conftest, тесты
main.py
README.md
README.ru.md
Dockerfile
docker-compose.yml
.env.example
requirements.txt
```

## Быстрый запуск

```bash
cp .env.example .env
docker compose up --build
```
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Mailhog: http://localhost:8025

## Переменные окружения
```
DATABASE_URL=postgresql+psycopg2://shop:shop@db:5432/shop
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
MAIL_HOST=mailhog
MAIL_PORT=1025
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Авторизация и роли

- user — каталог, корзина, свои заказы
- manager — товары, категории, обработка заказов
- admin — полный доступ

Защищённые ручки работают через JWT. Отозванные токены хранятся в Redis.

## Заказы
Обычный сценарий:

1. Пользователь кладёт товары в корзину
2. При оформлении заказа проверяется склад
3. Создаётся заказ
4. Оcтаток уменьшается
5. Celery отправляет письмо
6. Менеджер или админ меняет статус заказа

Если товара не хватает, API возвращает 409.

## Создание админа

Регистрация создаёт только обычного пользователя. Админа нужно назначить вручную.

```bash
docker compose exec db psql -U postgres -d shop
```

```SQL
UPDATE users
SET role = 'admin'
WHERE email = 'you@example.com';
```
## Тесты
```bash 
pytest 
```
Покрыто:

- основные сценарии и все публичные ручки
- регистрация и логин
- ограничения по ролям
- корзина и оформление заказа
- ошибка нехватки товара
- смена статуса заказа
- задача Celery на письмо

## Логирование

Сервис пишет в лог:

- неудачная регисрация
- неудачный логин
- созданный заказ
- конфликт по складу
- старт / успех / падение задачи Celery

Пароли и токены не логируются.

## Что показывает проект

- слоистая структура FastAPI
- JWT и разграничение ролей
- оформление заказа с проверкой склада
- Redis для черного списка токенов, broker 
- фоновые задачи через Celery
- локальный запуск в Docker
- интграционные тесты бизнес-сценариев
- CORS, rate limit

## Чего в проекте нет

- платёжный провайдер
- боевой SMTP
- Kubernetes
- фронтенд