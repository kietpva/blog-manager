# FastAPI Blog

Backend REST API for a blogging platform, built with FastAPI, SQLAlchemy, and PostgreSQL, featuring Clerk JWT authentication, RBAC (`admin`, `user`), and Clerk webhooks for user synchronization. Please follow this [plan](docs/PROJECT_PLAN.md).

## Key Features

- Clerk JWT authentication for protected endpoints.
- RBAC:
  - `user`: can create/update/delete their own posts and access allowed resources.
  - `admin`: can manage all users, posts, and categories.
- Post and category management (many-to-many via `post_categories`).
- Pagination for user/post listing (`limit`, `offset`).
- Clerk webhook endpoint to create internal users.

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic Settings
- Pytest
- Ruff
- uv (environment and dependency management)

## Project Structure

```text
fastapi-blog/
├── app/
│   ├── core/               # Config, constants, exceptions, logging
│   ├── db/                 # Session, init_db, base repository
│   ├── middleware/         # Authentication/processing middleware
│   ├── dependencies/       # FastAPI dependencies
│   ├── modules/            # auth, users, posts, categories, webhooks, health
│   └── utils/              # Helpers, pagination
├── alembic/                # Migration scripts
├── tests/                  # Unit/integration tests
├── docker-compose.yml      # PostgreSQL local
└── pyproject.toml
```

## Requirements

- Python `>= 3.13`
- Docker Desktop (to run local PostgreSQL)
- uv ([Installation guide](https://docs.astral.sh/uv/getting-started/installation/))

## Quick Start

1) Install dependencies

```bash
uv sync --all-groups
```

2) Create `.env` in the project root (`fastapi-blog/.env`)

```env
# Docker / Postgres
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=blog_db
POSTGRES_PORT=5432

# App
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/blog_db
DEBUG=true

# Clerk
CLERK_ISSUER=your_clerk_issuer
CLERK_JWKS_URL=your_clerk_jwks_url
CLERK_WEBHOOK_SECRET=your_clerk_webhook_secret
```

3) Start PostgreSQL with Docker

```bash
docker compose up -d
```

4) Run database migrations

```bash
uv run alembic upgrade head
```

5) Run the API

```bash
uv run fastapi dev app/main.py
```

After startup:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Main Endpoints

- `GET /health/`
- `GET /health/db`
- `POST /webhooks/clerk`

- `GET /users/{user_id}`
- `GET /users`
- `PATCH /users/{user_id}`

- `POST /posts`
- `GET /posts`
- `GET /posts/{post_id}`
- `PATCH /posts/{post_id}`
- `DELETE /posts/{post_id}`

- `POST /categories`
- `GET /categories`
- `GET /categories/{category_id}`
- `PATCH /categories/{category_id}`
- `DELETE /categories/{category_id}`

## Testing and Code Quality

Run tests:

```bash
uv run pytest
```

Run lint and format (ruff):

```bash
uv run ruff check .
uv run ruff format .
```

## Security Notes

- Do not commit `.env` (it contains secrets).
- If a webhook secret or key is exposed, rotate it in Clerk and update `.env`.

## Development Notes

- Keep routers thin, business logic in services, and DB access in repositories.
- Use schema mapping in responses; avoid returning raw ORM objects directly.
- When changing authorization logic, prioritize tests for RBAC and ownership checks.
