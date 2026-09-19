Русская версия: [README.ru.md](README.ru.md)

# Online Shop API

REST API for a small e-commerce service: catalog, cart, orders, roles, and email after checkout.

Built as a backend portfolio project. No frontend. The main interface is Swagger.

## Features

- Register / login with JWT
- Role-based access: user, manager, admin
- Product catalog and categories
- Cart
- Order checkout
- Order statuses
- Stock validation before purchase
- Redis: token storage / blacklist and rate limiting on IP
- Celery worker: send order email after checkout
- Mailhog for local email preview
- Structured logging for orders, auth failures, and worker tasks
- Integration tests for API endpoints and the email task
- Docker Compose: API, worker, PostgreSQL, Redis, Mailhog

## Tech stack

- Python 3.12
- FastAPI
- SQLAlchemy + PostgreSQL
- Pydantic
- Redis
- Celery
- Mailhog
- Pytest
- Docker / Docker Compose

## Architecture

```
client -> FastAPI
|-- PostgreSQL   (users, products, cart, orders)
|-- Redis        (tokens / rate limit / Celery broker)
`-- Celery worker -> Mailhog
```

Business rules live in services, not only in routers:

- a user cannot buy more items than stock
- stock decreases after a successful order
- order status can change only through allowed transitions
- admin / manager endpoints are protected by role checks,user cannot use them
- email is not sent inside the request: the API enqueues a Celery task

## Project structure

```bash
app/
├──api/           # routers
├──core/          # database, config, security, logging, rate limit, celery app
├──models/        # SQLAlchemy models
├──schemas/       # Pydantic schemas
├──services/      # business logic routers
├──tasks/         # tasks Celery
tests/            # conftest, tests
main.py
README.md
README.ru.md
Dockerfile
docker-compose.yml
.env.example
requirements.txt
```

## Quick start

```bash
cp .env.example .env
docker compose up --build
```
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Mailhog: http://localhost:8025

## Environment 
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

## Auth and roles

- user — catalog, cart, own orders
- manager — products, categories, order processing
- admin — full access

Protected routes use JWT. Refresh / revoked tokens are handled through Redis.

## Orders

Typical flow:

1. User adds products to cart
2. Checkout checks stock
3. Order is created
4. Stock is decreased
5. Celery task sends an email
6. Manager / admin can change order status

If stock is insufficient, the API returns 409.

## Create an admin

Registration creates a regular user. Promote an admin manually:

```bash
docker compose exec db psql -U postgres -d shop
```

```SQL
UPDATE users
SET role = 'admin'
WHERE email = 'you@example.com';
```

## Tests

```bash 
pytest 
```

Coverage includes:
- main scenarios and all public routers
- register and login
- role restrictions
- cart and checkout
- stock errors
- order status changes
- Celery email task

## Logging

The service logs:

- failed register
- failed login
- created orders
- stock conflicts
- Celery task start / success / failure

Passwords and tokens are not logged.

## What this project demonstrates

- layered FastAPI application
- JWT auth and RBAC
- transactional checkout with stock checks
- Redis for blacklist tokens,broker
- background jobs with Celery
- containerized local environment
- integration tests around business rules
- CORS, rate limit

## Not included

- real payment provider
- production SMTP
- Kubernetes
- frontend
