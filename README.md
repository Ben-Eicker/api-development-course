# API Development Course

[![Build and Deploy](https://github.com/Ben-Eicker/api-development-course/actions/workflows/build-deploy.yml/badge.svg)](https://github.com/Ben-Eicker/api-development-course/actions/workflows/build-deploy.yml)

A REST API built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, covering posts, user accounts, JWT authentication, and post voting.

A companion Streamlit frontend for this API lives in a separate repo: [frontend-development-course](https://github.com/Ben-Eicker/frontend-development-course). It's fully decoupled — it only talks to this API over HTTP — so the two are developed, versioned, and deployed independently. See that repo's README for setup.

## Features

- CRUD operations on posts (title, content, published flag)
- User registration and JWT-based login
- Post ownership enforcement (only the creator can update/delete a post)
- Upvoting/downvoting posts, with vote counts returned alongside each post
- Search, pagination (`limit`/`skip`), and title filtering on the posts list
- Database schema managed with Alembic migrations
- Config and secrets loaded from environment variables (never hardcoded)

## Tech stack

- [FastAPI](https://fastapi.tiangolo.com/) – web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) – ORM
- [Alembic](https://alembic.sqlalchemy.org/) – database migrations
- [PostgreSQL](https://www.postgresql.org/) – database
- [Pydantic](https://docs.pydantic.dev/) / [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) – request/response schemas and config
- [PyJWT](https://pyjwt.readthedocs.io/) + [pwdlib](https://frankie567.github.io/pwdlib/) – authentication and password hashing
- [Docker](https://www.docker.com/) – containerization
- [GitHub Actions](https://github.com/features/actions) – CI (lint + test) and image publishing
- [Ruff](https://docs.astral.sh/ruff/) – linting and formatting

## Project structure

```
app/
├── main.py         # FastAPI app instance, router registration
├── config.py        # Settings loaded from .env via pydantic-settings
├── database.py       # SQLAlchemy engine/session setup
├── models.py         # SQLAlchemy ORM models (Post, User, Vote)
├── schemas.py        # Pydantic request/response schemas
├── oauth2.py         # Password hashing, JWT creation/validation
└── routers/
    ├── post.py        # /posts endpoints
    ├── user.py        # /users endpoints
    ├── auth.py        # /login endpoint
    └── vote.py         # /vote endpoints
alembic/                # Database migration scripts
.github/workflows/      # CI/CD pipeline (lint, test, build, publish)
Dockerfile              # API container image
docker-compose-dev.yml  # Local dev stack (API + Postgres, live reload)
docker-compose-prod.yml # Production stack (pre-built image, no bind mounts)
requirements.txt        # Runtime dependencies (what Dockerfile installs)
requirements-dev.txt     # + test/lint tooling, for local dev and CI
ruff.toml               # Lint/format configuration
```

## Setup

There are two ways to run this project: with Docker (recommended, no local Postgres install needed) or fully locally.

### Option A: Docker

**1. Configure environment variables**

Create a `.env` file in the project root:

```env
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5433
DATABASE_NAME=api_development_course
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=<your-db-password>
SECRET_KEY=<a-random-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

POSTGRES_USER=postgres
POSTGRES_PASSWORD=<same-as-DATABASE_PASSWORD>
POSTGRES_DB=api_development_course
```

`.env` is gitignored — never commit real credentials. The Postgres container's host port is mapped to `5433` (not the default `5432`) to avoid clashing with a locally installed PostgreSQL service, if you have one.

**2. Start the containers**

```bash
docker compose -f docker-compose-dev.yml up --build
```

This builds the API image, starts Postgres, and runs `uvicorn` with `--reload` (code changes on your machine are picked up live via a bind mount).

**3. Run database migrations**

```bash
alembic upgrade head
```

Migrations run from your host machine against the containerized Postgres via the `5433` port mapping above.

The API is now available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

### Option B: Local (no Docker)

**1. Prerequisites**

- Python 3.13+
- A running PostgreSQL instance

**2. Install dependencies**

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements-dev.txt
```

`requirements-dev.txt` pulls in `requirements.txt` plus test/lint tooling (`pytest`, `ruff`). If you only need to run the API itself (e.g. building the Docker image), `requirements.txt` alone is enough — that's what `Dockerfile` installs.

**3. Configure environment variables**

Same as above, but set `DATABASE_PORT=5432` (or whatever port your local Postgres actually listens on) and `DATABASE_HOSTNAME=localhost`.

**4. Run database migrations**

```bash
alembic upgrade head
```

**5. Start the server**

```bash
uvicorn app.main:app --reload
```

## API overview

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/users/` | Register a new user | No |
| GET | `/users/{id}` | Get a user by id | No |
| POST | `/login/` | Log in, receive a JWT | No |
| GET | `/posts/` | List posts (supports `search`, `limit`, `skip`) | Yes |
| GET | `/posts/{id}` | Get a single post | Yes |
| POST | `/posts/` | Create a post | Yes |
| PUT | `/posts/{id}` | Update a post (owner only) | Yes |
| DELETE | `/posts/{id}` | Delete a post (owner only) | Yes |
| POST | `/vote/` | Vote (`dir: 1`) or remove a vote (`dir: 0`) on a post | Yes |

Authenticated requests must include `Authorization: Bearer <access_token>`, obtained from `POST /login`.

## Database migrations

Schema changes are made in `app/models.py`, then a migration is generated and applied:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

Always review autogenerated migrations before applying them — Alembic cannot detect column renames automatically and will generate a destructive drop/add instead of a rename.

## Running tests

```bash
pip install -r requirements-dev.txt   # if not already done
pytest
```

Tests run against a separate `_test`-suffixed database (see `app/tests/conftest.py`) and expect Postgres to be reachable — start it via `docker compose -f docker-compose-dev.yml up -d` first if it isn't running.

## CI/CD

Defined in `.github/workflows/build-deploy.yml`, two jobs:

1. **Lint & Test** — runs on every push and pull request targeting `main`. Spins up a throwaway Postgres service container, installs `requirements-dev.txt`, runs `ruff check .`, then `pytest`.
2. **Build & Push Docker Image** — runs only after Lint & Test passes, and only on a direct push to `main` (not on PRs). Builds the image from `Dockerfile` and pushes it to Docker Hub, tagged both `:latest` and with the commit SHA.

There is no automated deploy step — the pipeline stops at publishing the image to Docker Hub, since this project doesn't run on a live server.

To run this pipeline on your own fork, configure these under **Settings → Secrets and variables → Actions**:

**Secrets:**
- `DATABASE_PASSWORD`
- `SECRET_KEY`
- `DOCKERHUB_TOKEN` (a Docker Hub access token, not your account password)

**Variables:**
- `DATABASE_NAME`
- `DATABASE_USERNAME`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `DOCKERHUB_USERNAME`
