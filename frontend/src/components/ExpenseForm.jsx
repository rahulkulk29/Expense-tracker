import { useEffect, useState } from "react";
import { EXPENSE_CATEGORIES } from "../constants/categories";

const getTodayDate = () => new Date().toISOString().split("T")[0];

const INITIAL_FORM = {
  amount: "",
  category: "Food",
  description: "",
  expense_date: getTodayDate(),
};

export default function ExpenseForm({ editingExpense, onSave, onCancelEdit, isSubmitting }) {
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [validationError, setValidationError] = useState("");

  useEffect(() => {
    if (editingExpense) {
      setFormData({
        amount: String(editingExpense.amount),
        category: editingExpense.category,
        description: editingExpense.description || "",
        expense_date: editingExpense.expense_date,
      });
      setValidationError("");
    } else {
      setFormData({ ...INITIAL_FORM, expense_date: getTodayDate() });
      setValidationError("");
    }
  }, [editingExpense]);

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setValidationError("");
  }

  function validate() {
    const numericAmount = Number(formData.amount);
    if (!formData.amount || Number.isNaN(numericAmount) || numericAmount <= 0) {
      return "Amount must be a number greater than zero.";
    }
    if (!/^\d+(\.\d{1,2})?$/.test(formData.amount.trim())) {
      return "Amount cannot have more than 2 decimal places.";
    }
    if (!EXPENSE_CATEGORIES.includes(formData.category)) {
      return "Please select a valid category.";
    }
    if (formData.description.length > 250) {
      return "Description cannot exceed 250 characters.";
    }
    if (!formData.expense_date) {
      return "Expense date is required.";
    }
    return "";
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const error = validate();
    if (error) {
      setValidationError(error);
      return;
    }

    const payload = {
      amount: Number(formData.amount),
      category: formData.category,
      description: formData.description.trim() || null,
      expense_date: formData.expense_date,
    };

    const succeeded = await onSave(payload);
    if (succeeded && !editingExpense) {
      setFormData({ ...INITIAL_FORM, expense_date: getTodayDate() });
    }
  }

  return (
    <section className="card">
      <h2 className="section-title">
        {editingExpense ? "Edit Expense" : "Add Expense"}
      </h2>
      <form className="expense-form" onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <label htmlFor="amount">Amount *</label>
          <input
            id="amount"
            name="amount"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0.00"
            value={formData.amount}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="category">Category *</label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            required
          >
            {EXPENSE_CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="expense_date">Date *</label>
          <input
            id="expense_date"
            name="expense_date"
            type="date"
            value={formData.expense_date}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description (optional)</label>
          <input
            id="description"
            name="description"
            type="text"
            maxLength={250}
            placeholder="e.g. Lunch with team"
            value={formData.description}
            onChange={handleChange}
          />
        </div>

        {validationError && <p className="form-error">{validationError}</p>}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
            {isSubmitting
              ? "Saving..."
              : editingExpense
              ? "Update Expense"
              : "Save Expense"}
          </button>
          {editingExpense && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onCancelEdit}
              disabled={isSubmitting}
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </section>
  );
}

