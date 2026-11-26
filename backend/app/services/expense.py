from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.schemas.expense import ExpenseCategory, ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, payload: ExpenseCreate) -> Expense:
    """Persist a new expense record and return it."""
    expense = Expense(
        amount=payload.amount,
        category=payload.category.value,
        description=payload.description,
        expense_date=payload.expense_date,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def _apply_date_filters(query, start_date: Optional[date], end_date: Optional[date]):
    """Apply optional inclusive date range filters to an Expense query."""
    if start_date is not None:
        query = query.where(Expense.expense_date >= start_date)
    if end_date is not None:
        query = query.where(Expense.expense_date <= end_date)
    return query


def get_expenses(
    db: Session,
    category: Optional[ExpenseCategory] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[Expense]:
    """Return expenses matching optional category and date range filters."""
    query = select(Expense)
    if category is not None:
        query = query.where(Expense.category == category.value)
    query = _apply_date_filters(query, start_date, end_date)
    query = query.order_by(Expense.expense_date.desc(), Expense.id.desc())
    return list(db.scalars(query).all())


def get_expense_by_id(db: Session, expense_id: int) -> Optional[Expense]:
    """Fetch a single expense by primary key, or None if missing."""
    return db.get(Expense, expense_id)


def update_expense(db: Session, expense_id: int, payload: ExpenseUpdate) -> Optional[Expense]:
    """Replace editable fields on an existing expense, or return None if missing."""
    expense = db.get(Expense, expense_id)
    if expense is None:
        return None

    expense.amount = payload.amount
    expense.category = payload.category.value
    expense.description = payload.description
    expense.expense_date = payload.expense_date

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int) -> bool:
    """Delete an expense by ID. Returns True if deleted, False if not found."""
    expense = db.get(Expense, expense_id)
    if expense is None:
        return False

    db.delete(expense)
    db.commit()
    return True


def get_expense_summary(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> dict:
    """Compute total spending, expense count, and per-category totals."""
    query = select(
        Expense.category,
        func.sum(Expense.amount).label("category_total"),
        func.count(Expense.id).label("category_count"),
    )
    query = _apply_date_filters(query, start_date, end_date)
    query = query.group_by(Expense.category)

    rows = db.execute(query).all()
    if not rows:
        return {
            "total_expenses": Decimal("0"),
            "expense_count": 0,
            "category_summary": {},
        }

    total_expenses = Decimal("0")
    expense_count = 0
    category_summary: dict[str, Decimal] = {}

    for category, category_total, category_count in rows:
        amount_decimal = Decimal(category_total)
        category_summary[category] = amount_decimal
        total_expenses += amount_decimal
        expense_count += int(category_count)

    return {
        "total_expenses": total_expenses,
        "expense_count": expense_count,
        "category_summary": category_summary,
    }

