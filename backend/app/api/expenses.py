from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.expense import (
    ExpenseCategory,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseSummaryResponse,
    ExpenseUpdate,
)
from app.services import expense as expense_service

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def _validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> None:
    """Ensure start_date is not after end_date when both are provided."""
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be later than end_date",
        )


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
) -> ExpenseResponse:
    """Create a new expense."""
    return expense_service.create_expense(db, payload)


@router.get("", response_model=list[ExpenseResponse], status_code=status.HTTP_200_OK)
def list_expenses(
    category: Optional[ExpenseCategory] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
) -> list[ExpenseResponse]:
    """List expenses with optional category and date range filters."""
    _validate_date_range(start_date, end_date)
    return expense_service.get_expenses(db, category=category, start_date=start_date, end_date=end_date)


# Defined before /{expense_id} so 'summary' is not treated as an integer ID.
@router.get("/summary", response_model=ExpenseSummaryResponse, status_code=status.HTTP_200_OK)
def get_expense_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
) -> dict:
    """Return total spending, expense count, and category-wise breakdown."""
    _validate_date_range(start_date, end_date)
    return expense_service.get_expense_summary(db, start_date=start_date, end_date=end_date)


@router.get("/{expense_id}", response_model=ExpenseResponse, status_code=status.HTTP_200_OK)
def get_expense(
    expense_id: int = Path(..., gt=0, description="Positive integer ID of the expense"),
    db: Session = Depends(get_db),
) -> ExpenseResponse:
    """Retrieve a single expense by ID."""
    expense = expense_service.get_expense_by_id(db, expense_id)
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse, status_code=status.HTTP_200_OK)
def update_expense(
    payload: ExpenseUpdate,
    expense_id: int = Path(..., gt=0, description="Positive integer ID of the expense"),
    db: Session = Depends(get_db),
) -> ExpenseResponse:
    """Update an existing expense by ID."""
    expense = expense_service.update_expense(db, expense_id, payload)
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int = Path(..., gt=0, description="Positive integer ID of the expense"),
    db: Session = Depends(get_db),
) -> Response:
    """Delete an expense by ID."""
    deleted = expense_service.delete_expense(db, expense_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

