# PE Hackathon 2026 — Production Engineering Quest Completion

A Flask-based product management API built to survive production. This project demonstrates reliability, scalability, and incident response engineering across multiple quest tiers for the MLH Production Engineering Hackathon (April 2026).

## Architecture

```
                    ┌─────────────┐
                    │   Nginx     │
                    │Load Balancer│
                    │  (port 5000)│
                    └──────┬──────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         ┌──────┴──────┐       ┌──────┴──────┐
         │   App-1     │       │   App-2     │
         │  Gunicorn   │       │  Gunicorn   │
         │  (4 workers)│       │  (4 workers)│
         └──────┬──────┘       └──────┬──────┘
                │                     │
        ┌───────┴─────────────────────┴───────┐
        │                                     │
  ┌─────┴─────┐                        ┌──────┴──────┐
  │ PostgreSQL│                        │    Redis    │
  │   (DB)    │                        │   (Cache)   │
  └───────────┘                        └─────────────┘

        ┌─────────────┐
        │   Monitor   │ → Discord Webhook Alerts
        │ (monitor.py)│
        └─────────────┘
```

## Tech Stack

- **Backend:** Flask + Gunicorn (Python 3.13)
- **Database:** PostgreSQL 16 with Peewee ORM
- **Caching:** Redis 7 (30s TTL)
- **Load Balancer:** Nginx
- **Containerization:** Docker + Docker Compose (auto-restart)
- **CI/CD:** GitHub Actions (pytest on every push)
- **Testing:** pytest + pytest-cov (83% coverage, 19 tests)
- **Load Testing:** Locust
- **Monitoring:** Custom health monitor with Discord webhook alerts
- **Logging:** Structured JSON logging (python-json-logger)

## Quest Completion Summary

| Quest | Tier Achieved | Key Evidence |
|-------|--------------|--------------|
| Reliability Engineering | 🥇 Gold | 83% test coverage, CI/CD, chaos mode, graceful errors |
| Scalability Engineering | 🥇 Gold | 500 users @ 0% errors, Redis caching, Nginx LB |
| Incident Response | 🥈 Silver | JSON logging, /metrics, Discord alerting |
| Documentation | 🥈 Silver | README, deploy guide, troubleshooting, env vars, API docs |

---

## 🛡 Reliability Engineering — Gold

### Bronze: The Shield
- **Unit Tests:** 19 pytest tests covering models, routes, and error handling
- **CI/CD:** GitHub Actions runs tests on every commit — all runs passing green
- **Health Check:** `GET /health` returns `200 OK`

### Silver: The Fortress
- **83% Code Coverage:** Exceeds the 50% Silver and 70% Gold requirements
- **Integration Tests:** Tests hit the API directly (POST /products → verify DB state)
- **Gatekeeper CI:** Deployment blocked if tests fail
- **Error Handling:** 404s return `{"error": "Not found"}`, 500s return `{"error": "Internal server error"}`

### Gold: The Immortal
- **Coverage:** 83% total (app/\_\_init\_\_.py: 91%, database.py: 100%, models: 100%, routes/products.py: 81%)
- **Graceful Failure:** Bad inputs return clean JSON errors (e.g., `{"error": "Missing required fields: category, price"}`) — no stack traces
- **Chaos Mode:** `docker kill` the app container → Docker `restart: always` policy resurrects it automatically
- **Failure Manual:** See [docs/FAILURE_MODES.md](docs/FAILURE_MODES.md)

### Reliability Features
- **Input Validation:** All inputs validated, clean JSON errors returned
- **Unique Constraints:** Duplicate product names rejected (409)
- **Soft Deletes:** Data preserved, not destroyed
- **Global Error Handlers:** 404, 405, 500 — no stack traces exposed

---

## 🚀 Scalability Engineering — Gold

### Bronze: The Baseline
- **Load Test:** Locust with 50 concurrent users
- **Results:** 8.85 RPS, 0% failures, p95 ~4800ms (single Flask dev server)

### Silver: The Scale-Out
- **200 concurrent users** with 0% failures
- **Multi-container:** 2 app instances (app-1, app-2) via Docker Compose
- **Nginx Load Balancer:** Round-robin traffic distribution across containers
- **Response times:** p95 ~1300ms — well under the 3-second requirement

### Gold: The Speed of Light
- **500 concurrent users** at 76.72 req/s with **0% error rate**
- **Redis Caching:** `GET /products` served from Redis (30s TTL), reducing DB load
- **Gunicorn:** Replaced Flask dev server with Gunicorn (4 workers per container = 8 total)
- **Bottleneck Report:** See [docs/BOTTLENECK_REPORT.md](docs/BOTTLENECK_REPORT.md)

#### Before vs After Optimization

| Metric | Before (Flask Dev Server) | After (Gunicorn + Redis + Nginx) |
|--------|--------------------------|----------------------------------|
| Error Rate | 41.78% | 0.00% |
| Avg Response | 4,528 ms | 3,047 ms |
| Throughput | 57.51 req/s | 76.72 req/s |
| Max Response | 11,009 ms | 6,958 ms |

---

## 🚨 Incident Response — Silver

### Bronze: The Watchtower
- **Structured JSON Logging:** All logs include timestamps, log levels (INFO/WARN/ERROR), and component names
- **Metrics Endpoint:** `GET /metrics` returns real-time CPU, memory, and disk usage as JSON
- **Log Access:** `docker compose logs` — no SSH required

### Silver: The Alarm
- **Alert Configuration:** `alert_config.yaml` defines rules for "Service Down" (2 consecutive health check failures) and "High Error Rate" (>10%)
- **Discord Integration:** Alerts fire to a Discord webhook channel
- **Detection Speed:** Health checks every 30 seconds — alert fires within 60 seconds of failure
- **Monitor Service:** Runs as its own Docker container alongside the app

---

## 📜 Documentation — Bronze

- **README:** You're reading it
- **Architecture Diagram:** See above
- **API Docs:** See [docs/API.md](docs/API.md)
- **Failure Modes:** See [docs/FAILURE_MODES.md](docs/FAILURE_MODES.md)
- **Bottleneck Report:** See [docs/BOTTLENECK_REPORT.md](docs/BOTTLENECK_REPORT.md)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check — returns 200 OK |
| GET | `/metrics` | System metrics (CPU, memory, disk) |
| GET | `/products` | List all products (Redis-cached) |
| GET | `/products/:id` | Get single product |
| POST | `/products` | Create a new product |
| PUT | `/products/:id` | Update product |
| DELETE | `/products/:id` | Soft delete product |

See [docs/API.md](docs/API.md) for full API documentation.

---

## Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional for local dev) Python 3.13+, PostgreSQL, [uv](https://docs.astral.sh/uv/)

### Run with Docker (Recommended)
```bash
# Clone the repo
git clone https://github.com/Khine12/PE-Hackathon-Template-2026.git
cd PE-Hackathon-Template-2026

# Start all services (app x2, db, redis, nginx, monitor)
docker compose up -d --build

# Verify it's running
curl http://localhost:5000/health
# → {"status":"ok"}

# Run tests with coverage
docker compose exec app-1 uv run python -m pytest --cov=app --cov-report=term-missing

# Load test with Locust
uv run locust -f locustfile.py --host=http://localhost:5000
# Open http://localhost:8089, set users and ramp up
```

### Run Locally (Without Docker)
```bash
# Install dependencies
uv sync

# Create database
createdb hackathon_db

# Configure environment
cp .env.example .env

# Run the server
uv run run.py
```

## Deploy Guide

### Production Deploy
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart containers (zero-downtime)
docker compose down
docker compose up --build -d

# Verify the app is healthy
curl http://localhost:5000/health
# Expected: {"status": "ok"}
```

### Rollback (If Something Breaks)
```bash
# Find the last working commit
git log --oneline -5

# Roll back to it
git checkout <commit-hash>

# Rebuild with the old code
docker compose down
docker compose up --build -d

# Confirm health
curl http://localhost:5000/health
```

### Smoke Test After Deploy
```bash
# Check all containers are running
docker compose ps

# Tail logs for errors
docker compose logs --tail=50
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_NAME | hackathon_db | PostgreSQL database name |
| DATABASE_HOST | db | Database host |
| DATABASE_PORT | 5432 | Database port |
| DATABASE_USER | postgres | Database user |
| DATABASE_PASSWORD | postgres | Database password |
| REDIS_HOST | redis | Redis host |
| FLASK_DEBUG | false | Enable debug mode |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `psql: not recognized` | Use full path: `"C:\Program Files\PostgreSQL\16\bin\psql.exe"` |
| `password authentication failed` | Check DATABASE_PASSWORD in .env |
| `uv: not recognized` | Run: `$env:Path = "C:\Users\khine\.local\bin;$env:Path"` |
| `ModuleNotFoundError: app` | Make sure conftest.py exists in root directory |
| Docker WSL error | Run `wsl --update` in PowerShell |
| `No module named pytest` inside Docker | Use `docker compose exec app-1 uv run python -m pytest` |

## Project Structure

```
PE-Hackathon-Template-2026/
├── app/
│   ├── __init__.py          # App factory with error handlers
│   ├── cache.py             # Redis caching logic
│   ├── database.py          # PostgreSQL connection (Peewee ORM)
│   ├── logging_config.py    # Structured JSON logging
│   ├── models/
│   │   └── product.py       # Product model
│   └── routes/
│       ├── metrics.py       # /metrics endpoint
│       └── products.py      # /products CRUD routes
├── docs/
│   ├── API.md               # API documentation
│   ├── BOTTLENECK_REPORT.md # Scalability analysis
│   └── FAILURE_MODES.md     # Failure mode documentation
├── tests/
│   └── test_app.py          # 19 pytest tests
├── .github/workflows/       # CI pipeline
├── alert_config.yaml        # Alert rules configuration
├── docker-compose.yml       # Multi-container orchestration
├── Dockerfile               # App container definition
├── locustfile.py            # Load test scenarios
├── monitor.py               # Health check monitor + Discord alerts
├── nginx.conf               # Load balancer configuration
└── run.py                   # Development entry point
```

## Team

- **Khine Zar Hein** — Backend, Testing, CI/CD, Docker, Scalability, Monitoring, Documentation
- **Nicolas Tran** — Team Member
