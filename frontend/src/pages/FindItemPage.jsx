import { useState } from "react";

import { searchByFilters, searchByQuery } from "../api/itemsApi";
import ItemCard from "../components/ItemCard";


const emptyFilters = {
  item_name: "",
  category: "",
  color: "",
  found_location: "",
  date_from: "",
  date_to: "",
};


export default function FindItemPage() {
  const [mode, setMode] = useState("natural");
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState(emptyFilters);
  const [items, setItems] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function updateFilter(event) {
    setFilters((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const result = mode === "natural"
        ? await searchByQuery(query)
        : await searchByFilters(filters);
      setItems(result.items);
      setHasSearched(true);
    } catch (requestError) {
      setError(requestError.message);
      setItems([]);
      setHasSearched(false);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="find-page">
      <section className="find-hero">
        <div className="find-hero-inner">
          <div className="hero-copy">
            <p className="eyebrow">Campus lost &amp; found</p>
            <h1>Lost something? Start here.</h1>
            <p>Search verified campus reports in seconds, or report an item you found.</p>
          </div>
          <div className="hero-promise" aria-label="CampusFind highlights">
            <span><strong>01</strong> Search reports</span>
            <span><strong>02</strong> Match the details</span>
            <span><strong>03</strong> Track by reference</span>
          </div>
        </div>
      </section>

      <section className="search-panel search-card" aria-labelledby="search-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Search reports</p>
            <h2 id="search-title">What are you looking for?</h2>
          </div>
          <div className="mode-switch" aria-label="Search type">
            <button type="button" aria-pressed={mode === "natural"} className={mode === "natural" ? "selected" : ""} onClick={() => setMode("natural")}>Describe it</button>
            <button type="button" aria-pressed={mode === "manual"} className={mode === "manual" ? "selected" : ""} onClick={() => setMode("manual")}>Use filters</button>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {mode === "natural" ? (
            <div className="natural-search">
              <label htmlFor="query">Describe the item, color, or where it was found</label>
              <div className="search-row">
                <input id="query" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="e.g. Black earbuds case found at the Library" required />
                <button className="primary-button" disabled={loading}>{loading ? "Searching…" : "Search"}</button>
              </div>
              <p className="field-hint">English, Sinhala, and mixed phrases are supported when AI search is configured.</p>
            </div>
          ) : (
            <div className="form-grid search-form-grid">
              <label>Item name<input name="item_name" value={filters.item_name} onChange={updateFilter} placeholder="Earbuds case" /></label>
              <label>Category<input name="category" value={filters.category} onChange={updateFilter} placeholder="Electronics" /></label>
              <label>Color<input name="color" value={filters.color} onChange={updateFilter} placeholder="Black" /></label>
              <label>Location<input name="found_location" value={filters.found_location} onChange={updateFilter} placeholder="Library" /></label>
              <label>From date<input type="date" name="date_from" value={filters.date_from} onChange={updateFilter} /></label>
              <label>To date<input type="date" name="date_to" value={filters.date_to} onChange={updateFilter} /></label>
              <button className="primary-button form-action" disabled={loading}>{loading ? "Searching…" : "Search reports"}</button>
            </div>
          )}
        </form>
        {error && <div className="message error" role="alert">{error}</div>}
      </section>

      {hasSearched && (
        <section className="content-section results results-section" aria-live="polite">
          <div className="section-heading"><div><p className="eyebrow">Results</p><h2>{items.length} matching {items.length === 1 ? "report" : "reports"}</h2></div></div>
          {items.length ? <div className="card-grid">{items.map((item) => <ItemCard key={item.id} item={item} />)}</div> : <div className="empty-state"><h3>No matching items yet</h3><p>Try a broader item name or fewer filters.</p></div>}
        </section>
      )}
    </div>
  );
}
