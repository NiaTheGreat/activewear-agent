# Manufacturer Research Agent — Backend

FastAPI backend that wraps the activewear manufacturer research agent and exposes it as a REST API with JWT authentication, PostgreSQL persistence, and real-time search progress tracking.

## Prerequisites

- Python 3.12+
- PostgreSQL running (see `docker-compose.yml` in the project root)

## Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment variables
cp .env.example .env
# Edit .env with your actual keys

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000** with interactive docs at **http://localhost:8000/docs**.

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Create a new account |
| POST | `/api/auth/login` | Get JWT access token |
| GET | `/api/auth/me` | Current user info |

### Criteria Presets

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/presets` | List user's presets |
| POST | `/api/presets` | Create preset |
| GET | `/api/presets/{id}` | Get preset |
| PUT | `/api/presets/{id}` | Update preset |
| DELETE | `/api/presets/{id}` | Delete preset |

### Search

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/search/run` | Start a new search (async) |
| GET | `/api/search/{id}/status` | Poll search progress |
| GET | `/api/search/{id}` | Full search details |
| GET | `/api/search/history` | User's past searches |
| DELETE | `/api/search/{id}` | Delete search + manufacturers |

### Manufacturers

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/search/{search_id}/manufacturers` | List manufacturers (sort, filter) |
| GET | `/api/manufacturers/{id}` | Get single manufacturer |
| PUT | `/api/manufacturers/{id}` | Update notes, tags, favorite |

## Example Requests

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}'
```

### Start a Search

```bash
curl -X POST http://localhost:8000/api/search/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "criteria": {
      "locations": ["Vietnam", "Portugal"],
      "moq_min": 100,
      "moq_max": 500,
      "certifications_of_interest": ["GOTS", "OEKO-TEX"],
      "preferred_certifications": [],
      "materials": ["organic cotton", "recycled polyester"],
      "production_methods": ["sublimation", "screen printing"],
      "budget_tier": ["mid-range"],
      "additional_notes": null
    },
    "max_manufacturers": 5
  }'
```

### Poll Progress

```bash
curl http://localhost:8000/api/search/{search_id}/status \
  -H "Authorization: Bearer <token>"
```

### List Manufacturers

```bash
curl "http://localhost:8000/api/search/{search_id}/manufacturers?sort_by=match_score&sort_dir=desc&min_score=50" \
  -H "Authorization: Bearer <token>"
```

### Favorite a Manufacturer

```bash
curl -X PUT http://localhost:8000/api/manufacturers/{id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"is_favorite": true}'
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # pydantic-settings config
│   ├── database.py          # Async SQLAlchemy setup
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── api/                 # Route handlers
│   │   ├── deps.py          # Auth & DB dependencies
│   │   ├── auth.py
│   │   ├── presets.py
│   │   ├── search.py
│   │   └── manufacturers.py
│   ├── services/            # Business logic
│   │   ├── auth.py
│   │   └── agent_service.py # Agent pipeline wrapper
│   └── core/
│       └── security.py      # JWT & password hashing
├── alembic/                 # Database migrations
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── .env.example
```
