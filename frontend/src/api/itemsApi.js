const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");


async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(body.detail)
      ? body.detail.map((entry) => entry.msg).join(" ")
      : body.detail;
    throw new Error(detail || "The request could not be completed.");
  }
  return body;
}


export function searchByQuery(query) {
  return apiRequest("/api/items/search", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}


export function searchByFilters(filters) {
  const cleaned = Object.fromEntries(
    Object.entries(filters).filter(([, value]) => value !== ""),
  );
  return apiRequest("/api/items/search", {
    method: "POST",
    body: JSON.stringify({ filters: cleaned }),
  });
}


export function createReport(report) {
  return apiRequest("/api/items", {
    method: "POST",
    body: JSON.stringify(report),
  });
}


export function getReportStatus(referenceCode) {
  return apiRequest(`/api/items/${encodeURIComponent(referenceCode.trim())}`);
}
