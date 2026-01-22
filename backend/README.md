# Hellio HR Backend API

Backend API for Hellio HR candidate and position management system.

## Technology Stack

- **Framework**: FastAPI (Python 3.11)
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT tokens
- **Testing**: pytest + httpx

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Security, config
│   ├── db/              # Database session
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic
│   └── main.py          # FastAPI app
├── alembic/             # Database migrations
├── scripts/             # Import scripts, seed data
├── storage/documents/   # CV file storage
├── tests/               # All tests
├── data/                # Mock Excel/CSV files
└── docker-compose.yml   # MySQL + Backend services
```

## Setup

### 1. Install Dependencies

```bash
cd backend
poetry install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

### 3. Start MySQL Database

```bash
docker-compose up -d db
```

### 4. Run Migrations

```bash
poetry run alembic upgrade head
```

### 5. Create Admin User

```bash
poetry run python scripts/create_admin_user.py
```

### 6. Start API Server

```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## Docker Setup

Start both database and backend:

```bash
docker-compose up
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Testing

Run all tests:

```bash
poetry run pytest
```

With coverage:

```bash
poetry run pytest --cov=app --cov-report=html
```

## Authentication

Default admin credentials (for development):
- Email: admin@hellio.com
- Password: admin123

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user info

### Candidates
- `GET /api/v1/candidates` - List candidates (with search/filters)
- `GET /api/v1/candidates/{id}` - Get candidate details

### Positions
- `GET /api/v1/positions` - List positions (with search/filters)
- `GET /api/v1/positions/{id}` - Get position details
- `PUT /api/v1/positions/{id}` - Update position (requires editor role)

## Database Schema

See `app/models/` for complete schema. Key tables:
- `users` - Authentication and authorization
- `candidates` - Candidate profiles
- `positions` - Job positions
- `experiences` - Work experience
- `education` - Education history
- `skills` - Candidate skills
- `documents` - CV and document files
- `position_skills` - Required skills for positions
- `candidate_positions` - Many-to-many relationship

## Development

### Create New Migration

```bash
poetry run alembic revision --autogenerate -m "description"
```

### Apply Migration

```bash
poetry run alembic upgrade head
```

### Rollback Migration

```bash
poetry run alembic downgrade -1
```

## License

Proprietary - Hellio HR Team
