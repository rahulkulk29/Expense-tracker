const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"
).replace(/\/+$/, "");

function extractErrorMessage(data, fallbackMessage) {
  if (!data || typeof data !== "object") {
    return fallbackMessage;
  }
  if (typeof data.detail === "string") {
    return data.detail;
  }
  if (Array.isArray(data.detail) && data.detail.length > 0) {
    return data.detail
      .map((err) => {
        const field = Array.isArray(err.loc) ? err.loc[err.loc.length - 1] : "field";
        return `${field}: ${err.msg}`;
      })
      .join("; ");
  }
  return fallbackMessage;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (response.status === 204) {
    return null;
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const message = extractErrorMessage(
      data,
      `Request failed with status ${response.status}`
    );
    throw new Error(message);
  }

  return data;
}

function buildQueryString(params) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.append(key, value);
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

export function fetchExpenses(filters = {}) {
  const query = buildQueryString({
    category: filters.category,
    start_date: filters.startDate,
    end_date: filters.endDate,
  });
  return request(`/expenses${query}`);
}

export function fetchExpenseSummary(filters = {}) {
  const query = buildQueryString({
    start_date: filters.startDate,
    end_date: filters.endDate,
  });
  return request(`/expenses/summary${query}`);
}

export function createExpense(payload) {
  return request("/expenses", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateExpense(id, payload) {
  return request(`/expenses/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteExpense(id) {
  return request(`/expenses/${id}`, {
    method: "DELETE",
  });
}

