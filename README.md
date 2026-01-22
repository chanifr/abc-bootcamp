# Hellio HR - CV Management System

A full-stack HR candidate management system with a React frontend and FastAPI backend.

## Architecture

- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS
- **Backend**: Python 3.11 + FastAPI + SQLAlchemy 2.0
- **Database**: MySQL 8.0
- **Authentication**: JWT with role-based access control

## Features

- ✅ Candidate management (list, detail, search, filter)
- ✅ Position management (list, detail, update)
- ✅ Candidate-position relationships
- ✅ Side-by-side candidate comparison
- ✅ Role-based access (Admin, Editor, Read-only)
- ✅ RESTful API with OpenAPI documentation
- ✅ Responsive UI with modern design

## Quick Start with Docker Compose

### Prerequisites

- Docker and Docker Compose installed
- Ports 3000, 8000, and 3306 available

### Run the entire stack

```bash
# From the project root directory
docker compose up --build

# Or run in detached mode
docker compose up -d --build
```

This will start:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **MySQL**: localhost:3306

### Seed the database

```bash
# Run the seed script to populate with demo data
docker compose exec backend python scripts/seed_db.py
```

This creates:
- 3 users (admin, editor, viewer)
- 3 candidates (Sarah Chen, Michael Rodriguez, Emily Watson)
- 3 positions (Full-Stack Developer, DevOps Engineer, Product Manager)

### Default credentials

- **Admin**: admin@hellio.com / admin123
- **Editor**: editor@hellio.com / editor123
- **Viewer**: viewer@hellio.com / viewer123

### Stop the stack

```bash
docker compose down

# To also remove volumes (database data)
docker compose down -v
```

## Development Setup

### Backend Development

```bash
cd backend

# Install dependencies with Poetry
poetry install

# Run migrations
poetry run alembic upgrade head

# Seed database
poetry run python scripts/seed_db.py

# Run tests
poetry run pytest

# Start development server
poetry run uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:5173 or http://localhost:5174

## Project Structure

```
ABC/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Security, config
│   │   ├── db/              # Database setup
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── repositories/    # Data access layer
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   ├── scripts/             # Utility scripts
│   ├── storage/             # File storage
│   ├── tests/               # Test suite
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── types/           # TypeScript types
│   │   ├── utils/           # Utilities
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
└── docker-compose.yml       # Full stack orchestration
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Candidates
- `GET /api/v1/candidates` - List candidates (with filters)
- `GET /api/v1/candidates/{id}` - Get candidate details
- `POST /api/v1/candidates/{id}/positions/{position_id}` - Add position
- `DELETE /api/v1/candidates/{id}/positions/{position_id}` - Remove position

### Positions
- `GET /api/v1/positions` - List positions (with filters)
- `GET /api/v1/positions/{id}` - Get position details
- `PUT /api/v1/positions/{id}` - Update position (Editor+)

## Testing

### Backend Tests

```bash
cd backend
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html
```

Test coverage: **82%** (56 tests passing)

### Frontend Build

```bash
cd frontend
npm run build

# Preview production build
npm run preview
```

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=mysql+aiomysql://hellio:hellio123@localhost:3306/hellio_hr

# Security
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### CORS Issues
If you see CORS errors, ensure the frontend origin is in `ALLOWED_ORIGINS` in backend/.env

### Database Connection Issues
```bash
# Check if MySQL is running
docker compose ps

# View backend logs
docker compose logs backend

# Restart services
docker compose restart
```

### Port Conflicts
If ports are in use, modify the port mappings in docker-compose.yml

## License

This project is for educational/demonstration purposes.
