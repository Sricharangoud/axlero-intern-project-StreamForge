# StreamForge Database Project 🚀

Welcome to the **StreamForge** database design project! This project is designed to show you how to design a modern, relational database using **PostgreSQL**, map it to Python code using **SQLAlchemy 2.0 ORM**, manage migrations with **Alembic**, and write clean **CRUD (Create, Read, Update, Delete)** operations.

---

## Table of Contents
1. [Core Concepts Explained for Beginners](#1-core-concepts-explained-for-beginners)
2. [Project Architecture & Schema](#2-project-architecture--schema)
3. [Folder Structure](#3-folder-structure)
4. [Local Setup Guide](#4-local-setup-guide)
5. [Running Verification and Seeding](#5-running-verification-and-seeding)
6. [Managing Database Migrations with Alembic](#6-managing-database-migrations-with-alembic)

---

## 1. Core Concepts Explained for Beginners

### Relational Database (RDBMS) & PostgreSQL
A **relational database** stores data in tables (like Excel spreadsheets) with rows (records) and columns (attributes). Tables are linked together using **relationships** (foreign keys). 
* **PostgreSQL** is an enterprise-grade, highly reliable open-source relational database.
* In this project, we also support **SQLite** (a lightweight file-based database) out of the box so you can run the code instantly without installing PostgreSQL.

### Object Relational Mapping (ORM) & SQLAlchemy
In Python, writing raw SQL queries (`SELECT * FROM users WHERE...`) can be error-prone and hard to maintain. An **ORM** acts as a bridge:
* It maps database **tables** to Python **classes** (models).
* It maps table **rows** to Python **objects**.
* **SQLAlchemy** is the leading Python ORM. We use the modern **SQLAlchemy 2.0** syntax, which provides static type safety (`Mapped` and `mapped_column`) and clean query building.

### Database Migrations & Alembic
As your application grows, your database schema changes (e.g., adding a new column to a table). If you run `CREATE TABLE` again, you will lose existing data.
* **Database migrations** track changes to your database schema over time, like Git commits for database structure.
* **Alembic** is the migration tool for SQLAlchemy. It compares your models in Python with the database and automatically writes script files to upgrade or downgrade your database.

---

## 2. Project Architecture & Schema

StreamForge models the entities of a modern live-streaming platform:

* **Users**: Registered accounts.
* **Channels**: Streaming rooms owned by Users (**1:1 relationship**).
* **Categories**: Streaming games/topics (e.g. "Software Development", "Just Chatting").
* **Streams**: Active or past live broadcast sessions.
* **Follows**: Many-to-Many junction linking Users who follow Channels.
* **Subscriptions**: Premium backing ($) tier status linking Users and Channels.
* **Chat Messages**: Messages sent by viewers during a live broadcast.
* **Donations**: Monetary tips sent by viewers to streamers.

Refer to the visual layout of relationships in the project's design phase.

---

## 3. Folder Structure

```text
streamforge_db/
├── .env.example          # Template for database credentials
├── .env                  # Local file containing actual passwords (never commit this)
├── requirements.txt      # Python dependencies (SQLAlchemy, Alembic, psycopg2-binary, etc.)
├── verify_db.py          # Script to run unit-style verification tests (using in-memory SQLite)
├── alembic.ini           # Configuration file for Alembic
├── src/
│   ├── __init__.py       # Makes src a Python package
│   ├── config.py         # Config loader (.env -> Python variables)
│   ├── database.py       # SQLAlchemy engine and sessionmaker initialization
│   ├── models.py         # Database ORM models (tables, columns, relationships)
│   ├── crud.py           # Standard reusable Database query operations (Create/Read/Update/Delete)
│   └── seed.py           # Script to populate the database with realistic sample data
└── migrations/           # Alembic folder holding migration scripts and settings
    ├── env.py            # Tells Alembic how to connect to DB and where models are
    ├── script.py.mako    # Template file for generating migration scripts
    └── versions/         # Holds auto-generated migration history files
```

---

## 4. Local Setup Guide

### Step 1: Create a Virtual Environment
A virtual environment isolates your python dependencies.
```bash
# Create the environment
py -m venv .venv

# Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate it (Windows Command Prompt)
.venv\Scripts\activate.bat

# Activate it (macOS/Linux)
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup Configuration Environment
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
*If you don't have PostgreSQL set up, the code will automatically fall back to using a local SQLite file (`streamforge.db`) so you can explore immediately!*

---

## 5. Running Verification and Seeding

### Verify Schema & CRUD Operations (SQLite In-Memory)
We created a test suite that runs database schema generation and all CRUD functions in-memory. Run it with:
```bash
python verify_db.py
```
If successful, you will see a detailed checklist of passed assertions showing correct 1:1, M:N, and cascading behavior!

### Seed Sample Data
Populate your local database with mock channels, live streams, chat messages, and subscription tiers:
```bash
python -m src.seed
```
This will create a `streamforge.db` SQLite file locally (if you haven't configured a PostgreSQL server in `.env`) containing complete populated tables.

---

## 6. Managing Database Migrations with Alembic

If you connect to a PostgreSQL database, you will use **Alembic** to create tables and manage updates.

### Initialize Migrations (Done automatically or manually)
To initialize the migration directory (already configured in this project):
```bash
alembic init migrations
```

### Generate a Migration (Auto-detect model changes)
When you modify models in `src/models.py`, generate a new migration file:
```bash
alembic revision --autogenerate -m "Initial schema setup"
```
This generates a python file under `migrations/versions/` describing changes.

### Apply Migrations (Build/Update Database)
To apply pending migrations and build tables in PostgreSQL:
```bash
alembic upgrade head
```

### Rollback a Migration
If something went wrong, you can undo the last migration:
```bash
alembic downgrade -1
```
