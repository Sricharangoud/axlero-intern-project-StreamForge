# StreamForge 🚀 — Distributed Event Processing & Live Telemetry Platform

Welcome to **StreamForge**! StreamForge is a modern web application and backend system for real-time live streaming metrics and IoT sensor event processing.

---

## 📌 Table of Contents
1. [What is StreamForge?](#-what-is-streamforge)
2. [Technologies Explained Simply](#-technologies-explained-simply)
3. [Key Features](#-key-features)
4. [Folder Structure](#-folder-structure)
5. [Quick Start Guide (Run in 2 Minutes)](#-quick-start-guide-run-in-2-minutes)
6. [API Endpoints Cheat Sheet](#-api-endpoints-cheat-sheet)
7. [Testing & Database Commands](#-testing--database-commands)

---

## 💡 What is StreamForge?

**StreamForge** combines two real-time systems into one unified platform:
1. **Live Video Streaming Analytics:** Tracks video stream encoding quality (Bitrate, 1080p60 FPS, dropped frame %), live viewers, chat messages/min, and tip donations.
2. **IoT Sensor Monitoring:** Receives temperature and hardware sensor readings, detects spikes above safety limits (>75°C warning, >90°C critical), and raises alerts automatically.

---

## 🧠 Technologies Explained Simply

| Technology | What it is | Why we use it in StreamForge |
| :--- | :--- | :--- |
| **FastAPI** | High-speed Python Web Framework | Serves API endpoints fast with automatic Swagger documentation. |
| **Apache Kafka** | Distributed Streaming Message Queue | Ingests thousands of sensor events/sec without slowing down the server. |
| **PostgreSQL / SQLite** | Relational Database Engine | Stores persistent records for Users, Channels, Sensors, Alerts, and Streams. |
| **SQLAlchemy 2.0** | Python ORM (Object Relational Mapper) | Lets us write database queries using clean Python code instead of raw SQL strings. |
| **Alembic** | Database Migration Manager | Keeps track of database schema changes over time (like Git for database structure). |
| **Chart.js & HTML5** | Frontend Dashboard UI | Displays live interactive graphs, dark-mode glassmorphic cards, and real-time counters. |

---

## ✨ Key Features

- **🎥 Live Stream Telemetry Dashboard:** Displays active channels (AliceCodes, BobTheGamer, DevTalksLive) with real-time viewer count, stream resolution (`1080p60`), bitrate (`6000 kbps`), dropped frame %, and chat rates.
- **⚡ Interactive Simulator:** Click **"Simulate Viewer Spike"** on the dashboard (or send a POST request) to instantly test live traffic bursts and chart updates.
- **📟 IoT Hardware Monitoring:** Monitors server temperatures and automatically triggers open warning/critical alert tickets when thresholds are breached.
- **🔐 User Auth & Security:** Supports user sign-in using secure JSON Web Tokens (JWT) and encrypted passwords.
- **📊 Real-Time Charts:** Live Chart.js visualizations for throughput, sensor temperatures, encoding bitrate, and chat velocity.

---

## 📂 Folder Structure

The repository is organized into simple modular folders:

```text
StreamForge/
├── backend-api/           # Python FastAPI Web Backend
│   ├── app/api/v1/        # API Routes (auth, sensors, alerts, streams)
│   ├── app/models/        # Database Tables (User, Sensor, Alert, LiveStream)
│   ├── app/services/      # Business logic & simulation functions
│   └── app/main.py        # Backend server entry point
│
├── frontend-dashboard/     # Real-Time Telemetry Dashboard UI
│   ├── index.html         # Main Single Page Application (SPA)
│   └── js/                # Dashboard logic, API connection, & Chart.js scripts
│
├── frontend-auth/          # User Login Interface
│
├── query-core/             # Database ORM models & verification test suite
│   ├── src/models.py      # Core database schemas
│   └── verify_db.py       # Run this script to test database logic locally
│
└── query-migrations/       # Alembic Migration Files
```

---

## 🚀 Quick Start Guide (Run in 2 Minutes)

Follow these simple steps to run the complete platform on your computer:

### Step 1: Start the Backend API (FastAPI)

Open your terminal and run:

```bash
cd backend-api

# 1. Create a virtual environment (optional but recommended)
python -m venv .venv

# 2. Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Start the FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Swagger API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

### Step 2: Start the Frontend Dashboard

Open a **second terminal window** and run:

```bash
cd frontend-dashboard

# Start local web server on port 8080
python -m http.server 8080
```

Now open **[http://localhost:8080](http://localhost:8080)** in your browser!

#### 🔑 Demo Login Credentials:
- **Username / Email:** `admin` (or `admin@streamforge.com`)
- **Password:** `Admin@12345` (or `password123`)

---

## 🔌 API Endpoints Cheat Sheet

| HTTP Method | API Endpoint | What it does |
| :--- | :--- | :--- |
| `GET` | `/health` | Check if backend service is running |
| `POST` | `/api/v1/auth/login` | Sign in & receive access token |
| `GET` | `/api/v1/sensors/` | View list of all active server sensors |
| `POST` | `/api/v1/sensors/ingest` | Send new temperature reading |
| `GET` | `/api/v1/alerts/` | View open alerts and critical incidents |
| `GET` | `/api/v1/streams/live` | View live channels & video quality metrics |
| `GET` | `/api/v1/streams/analytics` | View total peak viewers & stream statistics |
| `POST` | `/api/v1/streams/simulate` | Trigger viewer spike / traffic burst simulation |

---

## 🧪 Testing & Database Commands

### Test Database Logic Locally (`query-core`)
```bash
cd query-core
python verify_db.py
```

### Apply Database Migrations (`query-migrations`)
```bash
cd query-migrations
alembic upgrade head
```

---

## 📝 License
Maintained as part of the **Axlero Internship Project**.
