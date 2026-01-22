# Hellio HR - Startup Guide

## 🚀 Starting the Application

You have **TWO options**:

### **Option 1: Complete Stack (Frontend + Backend + Database)**

From the **root ABC directory**:

```bash
cd /home/develeap/ABC

# Start everything (builds images first time)
docker compose up -d --build

# Check if services are running
docker compose ps

# Seed the database (first time only)
docker compose exec backend python scripts/seed_db.py
```

**What this starts:**
- ✅ MySQL Database on port 3306
- ✅ Backend API on port 8000
- ✅ Frontend on port 3000

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs

### **Option 2: Backend Only (Development Mode)**

From the **backend directory**:

```bash
cd /home/develeap/ABC/backend

# Start backend + database
docker compose up -d

# For frontend, run separately in another terminal
cd /home/develeap/ABC/frontend
npm run dev  # Runs on port 5173 or 5174
```

---

## 🛑 Stopping the Application

### **For Complete Stack:**

```bash
cd /home/develeap/ABC

# Stop all services (keeps data)
docker compose down

# Stop and remove ALL data (fresh start next time)
docker compose down -v
```

### **For Backend Only:**

```bash
cd /home/develeap/ABC/backend

# Stop backend + database
docker compose down

# Stop and remove data
docker compose down -v

# Stop frontend (Ctrl+C in the terminal where npm run dev is running)
```

---

## 📊 Useful Commands

### Viewing Status and Logs

```bash
# View running containers
docker compose ps

# View logs for all services
docker compose logs

# View logs for specific service
docker compose logs backend
docker compose logs frontend
docker compose logs db

# Follow logs in real-time
docker compose logs -f

# Follow logs for specific service
docker compose logs -f backend
```

### Restarting Services

```bash
# Restart all services
docker compose restart

# Restart a specific service
docker compose restart backend
docker compose restart frontend
docker compose restart db
```

### Rebuilding After Code Changes

```bash
# Rebuild and restart all services
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build backend
docker compose up -d --build frontend
```

### Executing Commands Inside Containers

```bash
# Seed the database
docker compose exec backend python scripts/seed_db.py

# Run backend tests
docker compose exec backend pytest

# Run backend tests with coverage
docker compose exec backend pytest --cov=app

# Access MySQL CLI
docker compose exec db mysql -u hellio -phellio123 hellio_hr

# Access backend shell
docker compose exec backend sh

# Run alembic migrations
docker compose exec backend alembic upgrade head
```

### Clean Up

```bash
# Stop and remove containers (keeps volumes/data)
docker compose down

# Stop and remove containers + volumes (removes all data)
docker compose down -v

# Remove all unused Docker resources
docker system prune -a

# View disk usage
docker system df
```

---

## 🔄 Switching Between Modes

### From Development Mode to Complete Stack:

```bash
# 1. Stop current backend
cd /home/develeap/ABC/backend
docker compose down

# 2. Stop frontend (Ctrl+C in that terminal)

# 3. Start complete stack from root
cd /home/develeap/ABC
docker compose up -d --build

# 4. Wait for services to start
sleep 5

# 5. Seed database (if needed)
docker compose exec backend python scripts/seed_db.py

# 6. Open browser to http://localhost:3000
```

### From Complete Stack to Development Mode:

```bash
# 1. Stop complete stack
cd /home/develeap/ABC
docker compose down

# 2. Start backend only
cd /home/develeap/ABC/backend
docker compose up -d

# 3. Start frontend in separate terminal
cd /home/develeap/ABC/frontend
npm run dev

# 4. Open browser to http://localhost:5173 or http://localhost:5174
```

---

## 💡 Quick Reference Table

| Action | Command | Location |
|--------|---------|----------|
| **Start complete stack** | `docker compose up -d` | `/home/develeap/ABC` |
| **Start backend only** | `docker compose up -d` | `/home/develeap/ABC/backend` |
| **Start frontend dev** | `npm run dev` | `/home/develeap/ABC/frontend` |
| **Stop all** | `docker compose down` | Root or backend dir |
| **View status** | `docker compose ps` | Root or backend dir |
| **View logs** | `docker compose logs -f` | Root or backend dir |
| **Rebuild** | `docker compose up -d --build` | Root or backend dir |
| **Fresh start** | `docker compose down -v && docker compose up -d --build` | Root or backend dir |
| **Seed data** | `docker compose exec backend python scripts/seed_db.py` | Root or backend dir |
| **Run tests** | `docker compose exec backend pytest` | Root or backend dir |

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check which services are running
docker compose ps

# Check logs for errors
docker compose logs

# Check specific service logs
docker compose logs backend
docker compose logs db

# Try fresh start
docker compose down -v
docker compose up -d --build
```

### Port Already in Use

```bash
# Check what's using port 3000 (frontend)
sudo lsof -i :3000

# Check what's using port 8000 (backend)
sudo lsof -i :8000

# Check what's using port 3306 (MySQL)
sudo lsof -i :3306

# Kill process using port (example)
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check if database is healthy
docker compose ps

# Check database logs
docker compose logs db

# Connect to database manually
docker compose exec db mysql -u hellio -phellio123 hellio_hr

# Reset database
docker compose down -v
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_db.py
```

### CORS Errors in Browser

```bash
# Check backend CORS configuration
docker compose logs backend | grep -i cors

# Ensure frontend origin is in ALLOWED_ORIGINS
# Edit backend/.env and add your frontend URL

# Restart backend
docker compose restart backend
```

### Frontend Not Loading

```bash
# Check if frontend container is running
docker compose ps frontend

# Check frontend logs
docker compose logs frontend

# Rebuild frontend
docker compose up -d --build frontend
```

### Changes Not Reflecting

```bash
# For backend changes (hot-reload enabled)
# Changes should reflect automatically

# For frontend changes in Docker
docker compose up -d --build frontend

# For frontend in dev mode (npm run dev)
# Changes should hot-reload automatically
```

---

## 📝 Default Credentials

- **Admin**: admin@hellio.com / admin123
- **Editor**: editor@hellio.com / editor123
- **Viewer**: viewer@hellio.com / viewer123

---

## 🎯 Common Workflows

### Daily Development

```bash
# Morning: Start services
docker compose up -d

# View logs while working
docker compose logs -f backend

# Evening: Stop services
docker compose down
```

### Testing Changes

```bash
# Run backend tests
docker compose exec backend pytest

# Run specific test file
docker compose exec backend pytest tests/api/test_candidates.py

# Run with coverage
docker compose exec backend pytest --cov=app --cov-report=html
```

### Fresh Database

```bash
# Reset everything
docker compose down -v
docker compose up -d
sleep 5
docker compose exec backend python scripts/seed_db.py
```

### Deploy to Production

```bash
# Build production images
docker compose -f docker-compose.yml build

# Push to registry (if using)
docker compose push

# Deploy
docker compose up -d
```
