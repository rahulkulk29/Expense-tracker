# Expense Tracker

A clean, beginner-friendly, single-user full-stack **Expense Tracker** web application built with **React (Vite)**, **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, containerized with **Docker Compose**.

## Features
- Add, view, edit, and delete personal expenses
- Filter expenses by category (`Food`, `Travel`, `Shopping`, `Bills`, `Entertainment`, `Other`) and date range
- Live dashboard showing total spending, expense count, and category-wise breakdown
- Server-side Pydantic validation and exact `Numeric(10, 2)` decimal currency storage
- Loading, empty, error, and success feedback states in the UI
- Automated `pytest` suite and Postman collection

## Tech Stack
- **Frontend:** React, JavaScript, Vite, CSS, Fetch API
- **Backend:** Python 3, FastAPI, Uvicorn, Pydantic
- **Database & ORM:** PostgreSQL 16, SQLAlchemy 2.0
- **Testing:** pytest, Postman
- **Containers:** Docker, Docker Compose

## Architecture

```mermaid
flowchart LR
    UI["React + Vite (5173)"] -->|Fetch API / JSON| API["FastAPI + Uvicorn (8000)"]
    API --> SVC["Service Layer"]
    SVC --> ORM["SQLAlchemy ORM"]
    ORM --> DB[("PostgreSQL (5432)")]
```

## Folder Structure & Module Responsibilities
- `backend/app/main.py` — FastAPI application setup, startup table creation, CORS, global error handlers, and `/health`.
- `backend/app/api/expenses.py` — HTTP route handlers under `/api/v1/expenses`.
- `backend/app/schemas/expense.py` — Pydantic request/response schemas and `ExpenseCategory` enum.
- `backend/app/services/expense.py` — Business logic for CRUD operations, filtering, and summary aggregation.
- `backend/app/models/expense.py` — SQLAlchemy `Expense` ORM model mapped to the `expenses` table.
- `backend/app/db/session.py` — Database engine, session factory, and `get_db` dependency.
- `backend/tests/` — Isolated `pytest` tests using an in-memory SQLite database.
- `frontend/src/services/api.js` — Centralized Fetch API client reading `VITE_API_BASE_URL`.
- `frontend/src/components/` — Reusable UI components (`SummaryCards`, `CategorySummary`, `ExpenseForm`, `ExpenseFilters`, `ExpenseList`).
- `postman/ExpenseTracker.postman_collection.json` — Ready-to-import Postman collection.
- `docs/` — [HLD](docs/HLD.md), [LLD](docs/LLD.md), and [API Contract](docs/API_CONTRACT.md).

## Prerequisites
- **For Docker:** Docker Desktop (with Docker Compose v2)
- **For Local Development (without Docker):** Python 3.12+, Node.js 20+, and a running PostgreSQL instance

## Environment Variables
Copy the example environment files before running locally:
- Root (Docker Compose): `.env.example` -> `.env`
- Backend: `backend/.env.example` -> `backend/.env`
- Frontend: `frontend/.env.example` -> `frontend/.env`

Key variables:
- `DATABASE_URL` — PostgreSQL connection string (e.g., `postgresql+psycopg://postgres:postgres@localhost:5432/expense_tracker`)
- `CORS_ORIGINS` — Comma-separated allowed origins (default: `http://localhost:5173,http://127.0.0.1:5173`)
- `VITE_API_BASE_URL` — Frontend API base URL (default: `http://localhost:8000/api/v1`)

## Running with Docker (Recommended)
1. Start all services (Frontend, Backend, PostgreSQL):
   ```bash
   docker compose up --build
   ```
2. Open the app:
   - Frontend: `http://localhost:5173`
   - Backend Swagger UI: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`
3. View logs:
   ```bash
   docker compose logs -f
   ```
4. Stop services (keeps database volume):
   ```bash
   docker compose down
   ```
5. Rebuild containers after code changes:
   ```bash
   docker compose up --build --force-recreate
   ```

## Local Development Setup (Without Docker)
### Running the Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Running the Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints
| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/expenses` | Create a new expense |
| `GET` | `/api/v1/expenses` | List expenses (supports `category`, `start_date`, `end_date`) |
| `GET` | `/api/v1/expenses/{expense_id}` | Get a single expense by ID |
| `PUT` | `/api/v1/expenses/{expense_id}` | Update an expense |
| `DELETE` | `/api/v1/expenses/{expense_id}` | Delete an expense |
| `GET` | `/api/v1/expenses/summary` | Get total spending, count, and category summary |

## Postman Instructions
1. Open Postman and click **Import**.
2. Select `postman/ExpenseTracker.postman_collection.json`.
3. Ensure the `baseUrl` collection variable is `http://localhost:8000`.
4. Run requests individually or use the **Collection Runner** to execute all status/field assertions.

## Running Tests
```bash
cd backend
pytest -v
```
Tests run against an isolated in-memory SQLite database so your development PostgreSQL data is never modified.

## Troubleshooting
- **CORS errors in browser:** Verify `CORS_ORIGINS` includes `http://localhost:5173`.
- **Database unavailable (`503`):** Ensure PostgreSQL is running and `DATABASE_URL` matches your credentials.
- **Port already in use:** Stop conflicting services on ports `5173`, `8000`, or `5432`.

