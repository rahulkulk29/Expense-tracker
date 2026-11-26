import { formatCurrency } from "./SummaryCards";

export default function ExpenseList({
  expenses,
  isLoading,
  onEdit,
  onDelete,
  deletingId,
}) {
  function handleDeleteClick(expense) {
    const label = expense.description
      ? `"${expense.description}" (${formatCurrency(expense.amount)})`
      : `${expense.category} (${formatCurrency(expense.amount)})`;
    if (window.confirm(`Delete expense ${label}?`)) {
      onDelete(expense.id);
    }
  }

  return (
    <section className="card">
      <h2 className="section-title">Expenses</h2>

      {isLoading ? (
        <p className="muted-text">Loading expenses...</p>
      ) : expenses.length === 0 ? (
        <div className="empty-state">
          <p>No expenses found.</p>
          <p className="muted-text">Add an expense or adjust your filters.</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="expense-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th className="align-right">Amount</th>
                <th className="align-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {expenses.map((expense) => (
                <tr key={expense.id}>
                  <td>{expense.expense_date}</td>
                  <td>{expense.description || <span className="muted-text">—</span>}</td>
                  <td>
                    <span className={`badge badge-${expense.category.toLowerCase()}`}>
                      {expense.category}
                    </span>
                  </td>
                  <td className="align-right amount-cell">
                    {formatCurrency(expense.amount)}
                  </td>
                  <td className="align-right actions-cell">
                    <button
                      type="button"
                      className="btn btn-small btn-secondary"
                      onClick={() => onEdit(expense)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="btn btn-small btn-danger"
                      onClick={() => handleDeleteClick(expense)}
                      disabled={deletingId === expense.id}
                    >
                      {deletingId === expense.id ? "Deleting..." : "Delete"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

