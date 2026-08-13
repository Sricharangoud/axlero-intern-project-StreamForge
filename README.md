# StreamForge 🚀 — Distributed Event Processing & Live Telemetry Platform

Welcome to **StreamForge** — an enterprise-ready, high-performance distributed event processor and live streaming telemetry platform built with **Python 3.10+**, **FastAPI**, **Apache Kafka**, **PostgreSQL / SQLAlchemy 2.0 ORM**, **Alembic**, and a modern **Glassmorphism Single Page Interface (SPA)**.

---

## 🌟 Key Features

- **⚡ Live Streaming & Video Telemetry Dashboard:** Real-time video encoding metrics (`1080p60 @ 6000 kbps`), dropped frame rates, peak concurrent viewers, chat message velocity (msgs/min), and total tip donations.
- **🎮 Interactive Simulation Engine:** Simulate live viewer spikes, bitrate drops, chat bursts, or tip donations via interactive dashboard buttons and API triggers (`POST /api/v1/streams/simulate`).
- **📟 IoT Telemetry & Kafka Stream Ingestion:** Ingest high-volume sensor event streams via Kafka producer/consumer pipelines with automated threshold triggers and incident alerting.
- **🔐 JWT Security & Auth System:** Production-ready JSON Web Token (JWT) authorization, password hashing (PBKDF2/Bcrypt), and role-based access control (Admin, Operator, Viewer).
- **📊 Interactive Data Visualizations:** Real-time throughput line charts, thermal heatmaps, encoding bitrate distributions, and chat velocity curves powered by Chart.js.
- **🗄️ Database ORM & Migrations:** Modular SQLAlchemy 2.0 async ORM design (`query-core`), schema migrations with Alembic (`query-migrations`), and automated DB seeding scripts.

---

## 📁 Repository Structure

```text
axlero-intern-project-StreamForge/
├── backend-api/           # FastAPI backend microservice (APIs, Auth, Sensors, Streams, Kafka Producer/Consumer)
│   ├── app/
│   │   ├── api/v1/        # Endpoints: auth, users, sensors, alerts, dashboard, streams
│   │   ├── core/          # Security, JWT auth, exception handlers, logging
│   │   ├── db/            # Async SQLAlchemy engine & session manager
│   │   ├── kafka/         # Kafka Producer & Consumer handlers
│   │   ├── models/        # ORM Models (User, Sensor, Alert, LiveStream)
│   │   ├── schemas/       # Pydantic validation schemas
│   │   └── services/      # Service business logic & simulation routines
│   └── main.py            # FastAPI entry point & startup db seeders
│
├── frontend-dashboard/     # Glassmorphic telemetry & streaming dashboard UI
│   ├── css/               # Modular CSS tokens, dark mode glassmorphism system
│   ├── js/                # API client, Chart.js controller, streams manager, router
│   └── index.html         # Main dashboard Single Page Application (SPA)
│
├── frontend-auth/          # Frontend authentication user interface
│
├── query-core/             # Database ORM models (SQLAlchemy 2.0), schemas, CRUD, & seeders
│   ├── src/               # Models, CRUD operations, configuration, seed script
│   └── verify_db.py       # Automated in-memory SQLite database verification suite
│
└── query-migrations/       # Database migration tracking and version management with Alembic
    └── migrations/        # Alembic schema version history
```

---

## 🛠️ Tech Stack

- **Backend Framework:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Messaging & Event Streaming:** Apache Kafka (Producer/Consumer)
- **Database & ORM:** PostgreSQL / SQLite, SQLAlchemy 2.0 (Async), Alembic Migrations
- **Frontend Architecture:** HTML5, Modern Vanilla JavaScript (ES6+), Chart.js, FontAwesome
- **Styling System:** Custom Vanilla CSS Design System with Dark Glassmorphism, HSL Color Palettes, & Micro-animations

---

## 🚀 Quick Start & Local Setup

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/Sricharangoud/axlero-intern-project-StreamForge.git
cd axlero-intern-project-StreamForge
```

---

### 3. Run the Backend API (`backend-api`)

```bash
cd backend-api

# Create and activate virtual environment
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Start FastAPI Uvicorn Server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Swagger Interactive API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Service Health Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

### 4. Run the Frontend Dashboard (`frontend-dashboard`)

Open a new terminal window:
```bash
cd frontend-dashboard

# Start local HTTP web server
python -m http.server 8080
```

Open **[http://localhost:8080](http://localhost:8080)** in your web browser.

#### Demo Login Credentials:
- **Username / Email:** `admin@streamforge.com` (or `admin`)
- **Password:** `Admin@12345` (or `password123`)

---

## 📡 API Endpoints Overview

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | System health check & service status |
| `/api/v1/auth/login` | `POST` | Authenticate user & obtain JWT Bearer Token |
| `/api/v1/sensors/` | `GET` / `POST` | List registered sensor nodes / Register new sensor |
| `/api/v1/sensors/ingest` | `POST` | Ingest real-time sensor measurement into Kafka stream |
| `/api/v1/alerts/` | `GET` | Retrieve active system alerts & threshold triggers |
| `/api/v1/streams/live` | `GET` | List active live broadcast channels & video quality metrics |
| `/api/v1/streams/analytics` | `GET` | Platform-wide video stream telemetry, peak viewers & chat velocity |
| `/api/v1/streams/simulate` | `POST` | Interactively simulate live viewer spikes & traffic bursts |

---

## 🧪 Database Verification & Migrations

### Run `query-core` Verification Suite
```bash
cd query-core
python verify_db.py
```

### Apply Database Migrations with Alembic
```bash
cd query-migrations
alembic upgrade head
```

---

## 📄 License
Maintained as part of the Axlero Internship project.
