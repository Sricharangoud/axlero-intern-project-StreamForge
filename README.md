# StreamForge 🚀

Welcome to **StreamForge** — a live-streaming platform project featuring a modular architecture with a FastAPI backend, Kafka integration, PostgreSQL/SQLAlchemy ORM database layer, Alembic migrations, and modular frontend dashboards.

---

## 📁 Repository Structure

```text
axlero-intern-project-StreamForge/
├── backend-api/           # FastAPI backend service (APIs, Auth, Sensors, Kafka Producer/Consumer)
├── frontend-auth/          # Frontend authentication user interface
├── frontend-dashboard/     # Frontend analytics and streaming dashboard UI
├── query-core/             # Database ORM models (SQLAlchemy 2.0), schemas, and CRUD operations
└── query-migrations/       # Database migration tracking and version management with Alembic
```

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, Kafka Producer/Consumer
- **Database & ORM:** PostgreSQL / SQLite, SQLAlchemy 2.0, Alembic Migrations
- **Frontend:** HTML5, CSS3 (Modern Glassmorphism Design System), Vanilla JavaScript (ES6+)
- **Testing & Verification:** Pytest / Native Verification Scripts

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

## 📦 Services Overview

### 1. `backend-api`
FastAPI backend service serving API endpoints for authentication, user management, sensors, alerts, dashboard statistics, and real-time Kafka messaging.

**Setup & Run:**
```bash
cd backend-api
python -m venv .venv
# Activate virtual environment
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

### 2. `frontend-auth` & `frontend-dashboard`
Modern frontend interfaces for user authentication and platform live streaming metrics dashboard.

**Setup & Run:**
Serve index.html using any local HTTP server (or Live Server extension in VS Code):
```bash
# Example using Python http.server
cd frontend-dashboard
python -m http.server 8000
```
Open `http://localhost:8000` in your browser.

---

### 3. `query-core`
Contains ORM models and CRUD methods for:
- Users & Channels
- Streams & Categories
- Follows & Subscriptions
- Chat Messages & Tip Donations

**Run Verification Suite:**
```bash
cd query-core
python verify_db.py
```

---

### 4. `query-migrations`
Contains Alembic database migrations tracking schema changes.

**Apply Migrations:**
```bash
cd query-migrations
alembic upgrade head
```

---

## 📄 License
This repository is maintained as part of the Axlero Internship project.
