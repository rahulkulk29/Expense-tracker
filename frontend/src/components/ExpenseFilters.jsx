import { EXPENSE_CATEGORIES } from "../constants/categories";

export default function ExpenseFilters({ filters, onChange, onClear }) {
  function handleFieldChange(event) {
    const { name, value } = event.target;
    onChange({ ...filters, [name]: value });
  }

  const hasActiveFilters = Boolean(
    filters.category || filters.startDate || filters.endDate
  );

  return (
    <section className="card filters-card" aria-label="Filter expenses">
      <div className="filters-grid">
        <div className="form-group">
          <label htmlFor="filter-category">Category</label>
          <select
            id="filter-category"
            name="category"
            value={filters.category}
            onChange={handleFieldChange}
          >
            <option value="">All Categories</option>
            {EXPENSE_CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="filter-start-date">Start Date</label>
          <input
            id="filter-start-date"
            name="startDate"
            type="date"
            value={filters.startDate}
            onChange={handleFieldChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="filter-end-date">End Date</label>
          <input
            id="filter-end-date"
            name="endDate"
            type="date"
            value={filters.endDate}
            onChange={handleFieldChange}
          />
        </div>

        <div className="filter-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClear}
            disabled={!hasActiveFilters}
          >
            Clear Filters
          </button>
        </div>
      </div>
    </section>
  );
}

