# Low-Level Design (LLD) — Expense Tracker

## 1. Project Folder Structure
```text
Expense-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, lifespan, CORS, global error handlers, /health
│   │   ├── api/expenses.py      # Route handlers under /api/v1/expenses
│   │   ├── schemas/expense.py   # Pydantic schemas and ExpenseCategory enum
│   │   ├── services/expense.py  # Business logic and SQLAlchemy queries
│   │   ├── models/expense.py    # Expense ORM model
│   │   └── db/session.py        # SQLAlchemy engine, SessionLocal, Base, get_db
│   ├── tests/
│   │   ├── conftest.py          # Isolated SQLite in-memory test fixtures
│   │   └── test_expenses.py     # Pytest suite for CRUD, filters, validation, summary
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.jsx             # React entry point
│   │   ├── App.jsx              # Dashboard state and layout orchestration
│   │   ├── index.css            # Application styles
│   │   ├── constants/categories.js
│   │   ├── services/api.js      # Centralized Fetch API client
│   │   └── components/
│   │       ├── SummaryCards.jsx
│   │       ├── CategorySummary.jsx
│   │       ├── ExpenseForm.jsx
│   │       ├── ExpenseFilters.jsx
│   │       └── ExpenseList.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── Dockerfile
├── postman/
│   └── ExpenseTracker.postman_collection.json
├── docs/
│   ├── HLD.md
│   ├── LLD.md
│   └── API_CONTRACT.md
├── docker-compose.yml
├── .env.example
└── README.md
```

## 2. Backend Module Responsibilities
- `app/db/session.py`: Reads `DATABASE_URL`, configures SQLAlchemy `engine` and `SessionLocal`, and provides `get_db()` dependency.
- `app/models/expense.py`: Maps the `expenses` table.
- `app/schemas/expense.py`: Defines `ExpenseCategory`, `ExpenseCreate`, `ExpenseUpdate`, `ExpenseResponse`, and `ExpenseSummaryResponse`.
- `app/services/expense.py`: Implements `create_expense`, `get_expenses`, `get_expense_by_id`, `update_expense`, `delete_expense`, and `get_expense_summary`.
- `app/api/expenses.py`: Maps HTTP routes to service functions and enforces date-range and positive-ID validation.
- `app/main.py`: Initializes database tables on startup, configures CORS, registers `/health` and `/api/v1/expenses`, and catches `OperationalError`/`SQLAlchemyError`/`Exception`.

## 3. Data Model (`expenses` table)
| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `INTEGER` | Primary Key, Indexed | Auto-incremented |
| `amount` | `NUMERIC(10, 2)` | Not Null | Exact decimal storage (> 0) |
| `category` | `VARCHAR(50)` | Not Null, Indexed | One of 6 predefined categories |
| `description` | `VARCHAR(250)` | Nullable | Optional trimmed note |
| `expense_date` | `DATE` | Not Null, Indexed | Date of expense |
| `created_at` | `TIMESTAMPTZ` | Not Null, `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | Not Null, `now()` | Auto-updated on change |

## 4. Validation Rules
- `amount`: `Decimal`, `> 0`, `max_digits=10`, `decimal_places=2`.
- `category`: Must match `ExpenseCategory` (`Food`, `Travel`, `Shopping`, `Bills`, `Entertainment`, `Other`).
- `description`: Optional string, max 250 characters; whitespace-only values normalize to `None`.
- `expense_date`: Required valid ISO date (`YYYY-MM-DD`).
- `expense_id`: Path integer `> 0`.
- `start_date` / `end_date`: When both are provided, `start_date <= end_date`.

## 5. Service Logic
- **Listing:** Applies optional `category`, `start_date >=`, and `end_date <=` filters, ordered by `expense_date DESC, id DESC`.
- **Summary:** Groups filtered records by `Expense.category` using `SUM(amount)` and `COUNT(id)` in `Decimal` arithmetic; returns zeros and `{}` when no records match.

## 6. Frontend Components
- `App.jsx`: Holds `expenses`, `summary`, `filters`, `editingExpense`, `isLoading`, `isSubmitting`, `deletingId`, `errorMessage`, and `successMessage`. Refreshes list + summary after every create, update, or delete.
- `ExpenseForm.jsx`: Handles Add and Edit modes with client-side validation.
- `ExpenseFilters.jsx`: Updates `category`, `startDate`, and `endDate` filters.
- `ExpenseList.jsx`: Renders table rows with Edit and Delete (with `window.confirm`) actions.
- `SummaryCards.jsx` & `CategorySummary.jsx`: Display total spending, count, and category progress bars.

## 7. Error Handling
- **Backend:** Pydantic returns `422` for schema/query errors; missing IDs raise `404` (`{"detail": "Expense not found"}`); `OperationalError` returns `503`; unhandled exceptions return `500` without stack traces.
- **Frontend:** `src/services/api.js` parses FastAPI `detail` strings or validation error arrays into readable `Error` messages shown in a dismissible alert banner.

## 8. Testing Plan
- **Automated (`pytest`):** Isolated SQLite in-memory DB tests covering health check, valid/invalid creation, listing/ordering, filtering, ID lookup, 404 handling, update, delete, summary calculation, and empty summary.
- **Manual (`Postman`):** 14-request collection verifying status codes and response fields against a running backend.

