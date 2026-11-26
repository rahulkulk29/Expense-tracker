# API Contract — Expense Tracker

## Base URL
- Local Backend Root: `http://localhost:8000`
- Expense API Base Path: `http://localhost:8000/api/v1`
- Interactive Swagger UI: `http://localhost:8000/docs`

## Supported Categories
`Food`, `Travel`, `Shopping`, `Bills`, `Entertainment`, `Other`

## Endpoints Overview
| Method | Path | Description | Success Code |
| --- | --- | --- | --- |
| `GET` | `/health` | Health check | `200` |
| `POST` | `/api/v1/expenses` | Create expense | `201` |
| `GET` | `/api/v1/expenses` | List & filter expenses | `200` |
| `GET` | `/api/v1/expenses/{expense_id}` | Get expense by ID | `200` |
| `PUT` | `/api/v1/expenses/{expense_id}` | Update expense | `200` |
| `DELETE` | `/api/v1/expenses/{expense_id}` | Delete expense | `204` |
| `GET` | `/api/v1/expenses/summary` | Get spending summary | `200` |

---

## 1. Health Check
`GET /health`

**Response (`200 OK`):**
```json
{
  "status": "healthy"
}
```

## 2. Create Expense
`POST /api/v1/expenses`

**Request Body:**
```json
{
  "amount": 500.00,
  "category": "Food",
  "description": "Lunch",
  "expense_date": "2026-11-26"
}
```

**Response (`201 Created`):**
```json
{
  "id": 1,
  "amount": 500.0,
  "category": "Food",
  "description": "Lunch",
  "expense_date": "2026-11-26",
  "created_at": "2026-11-26T10:00:00Z",
  "updated_at": "2026-11-26T10:00:00Z"
}
```

**Validation Errors (`422 Unprocessable Entity`):**
Returned when `amount <= 0`, `amount` has > 2 decimal places, `category` is unsupported, `description` > 250 chars, or `expense_date` is missing/invalid.

## 3. Get All Expenses
`GET /api/v1/expenses`

**Optional Query Parameters:**
- `category` (one of the 6 supported categories)
- `start_date` (`YYYY-MM-DD`)
- `end_date` (`YYYY-MM-DD`)

**Response (`200 OK`):**
JSON array of expense objects ordered by `expense_date` descending, then `id` descending. Returns `[]` if empty.

**Error (`422 Unprocessable Entity`):**
Returned if `start_date` is later than `end_date` or if query parameter formats are invalid.

## 4. Get Expense By ID
`GET /api/v1/expenses/{expense_id}`

**Response (`200 OK`):** Single expense object.

**Error (`404 Not Found`):**
```json
{
  "detail": "Expense not found"
}
```

## 5. Update Expense
`PUT /api/v1/expenses/{expense_id}`

**Request Body:**
```json
{
  "amount": 600.00,
  "category": "Food",
  "description": "Dinner",
  "expense_date": "2026-11-26"
}
```

**Response (`200 OK`):** Updated expense object.

**Errors:** `404 Not Found` if ID does not exist; `422 Unprocessable Entity` for invalid body.

## 6. Delete Expense
`DELETE /api/v1/expenses/{expense_id}`

**Response (`204 No Content`):** Empty body.

**Error (`404 Not Found`):**
```json
{
  "detail": "Expense not found"
}
```

## 7. Expense Summary
`GET /api/v1/expenses/summary`

**Optional Query Parameters:**
- `start_date` (`YYYY-MM-DD`)
- `end_date` (`YYYY-MM-DD`)

**Response (`200 OK`):**
```json
{
  "total_expenses": 1420.5,
  "expense_count": 4,
  "category_summary": {
    "Food": 700.0,
    "Travel": 120.0,
    "Shopping": 600.5
  }
}
```

**Empty State (`200 OK`):**
```json
{
  "total_expenses": 0,
  "expense_count": 0,
  "category_summary": {}
}
```

## HTTP Status Codes Summary
- `200` — Successful retrieval or update
- `201` — Expense created
- `204` — Expense deleted (empty body)
- `404` — Expense ID or route not found
- `405` — Unsupported HTTP method
- `422` — Validation error (body, query, or path)
- `500` — Unexpected internal server error (`{"detail": "Internal server error"}`)
- `503` — Database unavailable (`{"detail": "Database service unavailable"}`)

