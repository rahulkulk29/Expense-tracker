import { formatCurrency } from "./SummaryCards";

export default function CategorySummary({ categorySummary, totalExpenses }) {
  const entries = Object.entries(categorySummary || {}).sort((a, b) => b[1] - a[1]);

  return (
    <section className="card">
      <h2 className="section-title">Category Summary</h2>
      {entries.length === 0 ? (
        <p className="muted-text">No category spending data for the selected range.</p>
      ) : (
        <ul className="category-list">
          {entries.map(([category, amount]) => {
            const percentage =
              totalExpenses > 0 ? Math.round((Number(amount) / Number(totalExpenses)) * 100) : 0;
            return (
              <li key={category} className="category-item">
                <div className="category-row">
                  <span className={`badge badge-${category.toLowerCase()}`}>{category}</span>
                  <span className="category-amount">
                    {formatCurrency(amount)} ({percentage}%)
                  </span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${percentage}%` }} />
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

