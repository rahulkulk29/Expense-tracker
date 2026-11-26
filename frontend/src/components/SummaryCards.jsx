export function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(amount || 0));
}

export default function SummaryCards({ totalExpenses, expenseCount }) {
  return (
    <section className="summary-cards" aria-label="Expense summary">
      <div className="card stat-card">
        <span className="stat-label">Total Spending</span>
        <strong className="stat-value">{formatCurrency(totalExpenses)}</strong>
      </div>
      <div className="card stat-card">
        <span className="stat-label">Number of Expenses</span>
        <strong className="stat-value">{expenseCount}</strong>
      </div>
    </section>
  );
}

