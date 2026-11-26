import { useCallback, useEffect, useState } from "react";
import CategorySummary from "./components/CategorySummary";
import ExpenseFilters from "./components/ExpenseFilters";
import ExpenseForm from "./components/ExpenseForm";
import ExpenseList from "./components/ExpenseList";
import SummaryCards from "./components/SummaryCards";
import {
  createExpense,
  deleteExpense,
  fetchExpenses,
  fetchExpenseSummary,
  updateExpense,
} from "./services/api";

const EMPTY_FILTERS = {
  category: "",
  startDate: "",
  endDate: "",
};

export default function App() {
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState({
    total_expenses: 0,
    expense_count: 0,
    category_summary: {},
  });
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [editingExpense, setEditingExpense] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadDashboardData = useCallback(async (activeFilters) => {
    if (
      activeFilters.startDate &&
      activeFilters.endDate &&
      activeFilters.startDate > activeFilters.endDate
    ) {
      setErrorMessage("Start date cannot be later than end date.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    try {
      const [expensesData, summaryData] = await Promise.all([
        fetchExpenses(activeFilters),
        fetchExpenseSummary(activeFilters),
      ]);
      setExpenses(expensesData);
      setSummary(summaryData);
    } catch (err) {
      setErrorMessage(err.message || "Failed to load expenses.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData(filters);
  }, [filters, loadDashboardData]);

  async function handleSaveExpense(payload) {
    setIsSubmitting(true);
    setErrorMessage("");
    setSuccessMessage("");
    try {
      if (editingExpense) {
        await updateExpense(editingExpense.id, payload);
        setSuccessMessage("Expense updated successfully.");
        setEditingExpense(null);
      } else {
        await createExpense(payload);
        setSuccessMessage("Expense added successfully.");
      }
      await loadDashboardData(filters);
      return true;
    } catch (err) {
      setErrorMessage(err.message || "Failed to save expense.");
      return false;
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeleteExpense(expenseId) {
    setDeletingId(expenseId);
    setErrorMessage("");
    setSuccessMessage("");
    try {
      await deleteExpense(expenseId);
      if (editingExpense && editingExpense.id === expenseId) {
        setEditingExpense(null);
      }
      setSuccessMessage("Expense deleted successfully.");
      await loadDashboardData(filters);
    } catch (err) {
      setErrorMessage(err.message || "Failed to delete expense.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div>
          <h1>Expense Tracker</h1>
          <p className="subtitle">Track, filter, and analyze your personal spending</p>
        </div>
      </header>

      {errorMessage && (
        <div className="alert alert-error" role="alert">
          <span>{errorMessage}</span>
          <button
            type="button"
            className="alert-close"
            onClick={() => setErrorMessage("")}
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success" role="status">
          <span>{successMessage}</span>
          <button
            type="button"
            className="alert-close"
            onClick={() => setSuccessMessage("")}
            aria-label="Dismiss message"
          >
            ×
          </button>
        </div>
      )}

      <SummaryCards
        totalExpenses={summary.total_expenses}
        expenseCount={summary.expense_count}
      />

      <div className="main-grid">
        <div className="left-column">
          <ExpenseForm
            editingExpense={editingExpense}
            onSave={handleSaveExpense}
            onCancelEdit={() => setEditingExpense(null)}
            isSubmitting={isSubmitting}
          />
          <CategorySummary
            categorySummary={summary.category_summary}
            totalExpenses={summary.total_expenses}
          />
        </div>

        <div className="right-column">
          <ExpenseFilters
            filters={filters}
            onChange={setFilters}
            onClear={() => setFilters(EMPTY_FILTERS)}
          />
          <ExpenseList
            expenses={expenses}
            isLoading={isLoading}
            onEdit={(expense) => {
              setEditingExpense(expense);
              setSuccessMessage("");
            }}
            onDelete={handleDeleteExpense}
            deletingId={deletingId}
          />
        </div>
      </div>
    </div>
  );
}

