from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_expense_valid(client: TestClient) -> None:
    payload = {
        "amount": 500.00,
        "category": "Food",
        "description": "Lunch",
        "expense_date": "2026-11-26",
    }
    response = client.post("/api/v1/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["amount"] == 500.00
    assert data["category"] == "Food"
    assert data["description"] == "Lunch"
    assert data["expense_date"] == "2026-11-26"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_expense_invalid_amount(client: TestClient) -> None:
    for bad_amount in [0, -25.5, 12.345]:
        response = client.post(
            "/api/v1/expenses",
            json={
                "amount": bad_amount,
                "category": "Food",
                "description": "Invalid",
                "expense_date": "2026-11-26",
            },
        )
        assert response.status_code == 422


def test_create_expense_invalid_category(client: TestClient) -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": 50.00,
            "category": "Crypto",
            "description": "Unsupported",
            "expense_date": "2026-11-26",
        },
    )
    assert response.status_code == 422


def test_list_expenses_and_ordering(client: TestClient) -> None:
    client.post(
        "/api/v1/expenses",
        json={"amount": 100.00, "category": "Food", "description": "Older", "expense_date": "2026-11-20"},
    )
    client.post(
        "/api/v1/expenses",
        json={"amount": 200.00, "category": "Travel", "description": "Newer 1", "expense_date": "2026-11-25"},
    )
    client.post(
        "/api/v1/expenses",
        json={"amount": 300.00, "category": "Bills", "description": "Newer 2", "expense_date": "2026-11-25"},
    )

    response = client.get("/api/v1/expenses")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 3
    assert [item["description"] for item in items] == ["Newer 2", "Newer 1", "Older"]


def test_filter_expenses(client: TestClient) -> None:
    client.post(
        "/api/v1/expenses",
        json={"amount": 100.00, "category": "Food", "description": "Nov 1", "expense_date": "2026-11-01"},
    )
    client.post(
        "/api/v1/expenses",
        json={"amount": 250.00, "category": "Food", "description": "Nov 15", "expense_date": "2026-11-15"},
    )
    client.post(
        "/api/v1/expenses",
        json={"amount": 80.00, "category": "Travel", "description": "Nov 15", "expense_date": "2026-11-15"},
    )

    cat_resp = client.get("/api/v1/expenses?category=Food")
    assert cat_resp.status_code == 200
    assert len(cat_resp.json()) == 2

    range_resp = client.get("/api/v1/expenses?category=Food&start_date=2026-11-10&end_date=2026-11-30")
    assert range_resp.status_code == 200
    assert len(range_resp.json()) == 1
    assert range_resp.json()[0]["description"] == "Nov 15"

    bad_range = client.get("/api/v1/expenses?start_date=2026-11-20&end_date=2026-11-01")
    assert bad_range.status_code == 422


def test_get_expense_by_id_and_404(client: TestClient) -> None:
    created = client.post(
        "/api/v1/expenses",
        json={"amount": 45.50, "category": "Other", "description": "Coffee", "expense_date": "2026-11-26"},
    ).json()

    found = client.get(f"/api/v1/expenses/{created['id']}")
    assert found.status_code == 200
    assert found.json()["amount"] == 45.50

    missing = client.get("/api/v1/expenses/9999")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Expense not found"}


def test_update_expense(client: TestClient) -> None:
    created = client.post(
        "/api/v1/expenses",
        json={"amount": 500.00, "category": "Food", "description": "Lunch", "expense_date": "2026-11-26"},
    ).json()

    updated = client.put(
        f"/api/v1/expenses/{created['id']}",
        json={"amount": 600.00, "category": "Food", "description": "Dinner", "expense_date": "2026-11-26"},
    )
    assert updated.status_code == 200
    assert updated.json()["amount"] == 600.00
    assert updated.json()["description"] == "Dinner"

    missing = client.put(
        "/api/v1/expenses/9999",
        json={"amount": 600.00, "category": "Food", "description": "Dinner", "expense_date": "2026-11-26"},
    )
    assert missing.status_code == 404


def test_delete_expense(client: TestClient) -> None:
    created = client.post(
        "/api/v1/expenses",
        json={"amount": 75.00, "category": "Shopping", "description": "Book", "expense_date": "2026-11-26"},
    ).json()

    deleted = client.delete(f"/api/v1/expenses/{created['id']}")
    assert deleted.status_code == 204
    assert deleted.text == ""

    after_delete = client.get(f"/api/v1/expenses/{created['id']}")
    assert after_delete.status_code == 404

    missing_delete = client.delete("/api/v1/expenses/9999")
    assert missing_delete.status_code == 404


def test_expense_summary_and_empty_summary(client: TestClient) -> None:
    empty_resp = client.get("/api/v1/expenses/summary")
    assert empty_resp.status_code == 200
    assert empty_resp.json() == {
        "total_expenses": 0,
        "expense_count": 0,
        "category_summary": {},
    }

    client.post(
        "/api/v1/expenses",
        json={"amount": 500.00, "category": "Food", "description": "Lunch", "expense_date": "2026-11-25"},
    )
    client.post(
        "/api/v1/expenses",
        json={"amount": 200.00, "category": "Food", "description": "Dinner", "expense_date": "2026-11-26"},
    )
    client.post(
        "/api/v1/expenses",
        json={"amount": 120.00, "category": "Travel", "description": "Cab", "expense_date": "2026-11-26"},
    )
    client.post(
        "/api/v1/expenses",
        json={"amount": 600.50, "category": "Shopping", "description": "Shoes", "expense_date": "2026-11-26"},
    )

    summary_resp = client.get("/api/v1/expenses/summary")
    assert summary_resp.status_code == 200
    assert summary_resp.json() == {
        "total_expenses": 1420.50,
        "expense_count": 4,
        "category_summary": {
            "Food": 700.00,
            "Travel": 120.00,
            "Shopping": 600.50,
        },
    }

    bad_range = client.get("/api/v1/expenses/summary?start_date=2026-11-30&end_date=2026-11-01")
    assert bad_range.status_code == 422

