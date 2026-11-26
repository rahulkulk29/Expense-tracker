from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, field_validator


class ExpenseCategory(str, Enum):
    """Predefined expense categories supported by the application."""

    FOOD = "Food"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    BILLS = "Bills"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"


# Keep Decimal precision in Python/DB while serializing to JSON numbers per API contract.
MonetaryInput = Annotated[
    Decimal,
    Field(gt=0, max_digits=10, decimal_places=2),
]

MonetaryOutput = Annotated[
    Decimal,
    PlainSerializer(lambda value: float(round(value, 2)), return_type=float, when_used="json"),
]


class ExpenseBase(BaseModel):
    """Shared validation rules for creating and updating an expense."""

    amount: MonetaryInput
    category: ExpenseCategory
    description: Optional[str] = Field(default=None, max_length=250)
    expense_date: date

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None


class ExpenseCreate(ExpenseBase):
    """Request schema for creating a new expense."""


class ExpenseUpdate(ExpenseBase):
    """Request schema for replacing an existing expense via PUT."""


class ExpenseResponse(BaseModel):
    """Response schema returned for a single expense."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: MonetaryOutput
    category: ExpenseCategory
    description: Optional[str]
    expense_date: date
    created_at: datetime
    updated_at: datetime


class ExpenseSummaryResponse(BaseModel):
    """Aggregated spending summary across expenses."""

    total_expenses: MonetaryOutput
    expense_count: int
    category_summary: dict[str, MonetaryOutput]

