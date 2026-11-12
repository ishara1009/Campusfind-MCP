import { useState } from "react";

import { getReportStatus } from "../api/itemsApi";
import ItemCard from "../components/ItemCard";


export default function ReportStatusPage() {
  const [referenceCode, setReferenceCode] = useState("");
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setItem(null);
    try {
      const result = await getReportStatus(referenceCode);
      setItem(result.item);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="status-page">
      <div className="status-header">
        <p className="eyebrow">Report lookup</p>
        <h1>Check report status.</h1>
        <p>Enter the reference code created when the item was reported.</p>
      </div>
      <div className="status-search-card">
        <form onSubmit={handleSubmit}>
          <label htmlFor="reference-code">Reference code</label>
          <div className="search-row">
            <input id="reference-code" value={referenceCode} onChange={(event) => setReferenceCode(event.target.value.toUpperCase())} placeholder="CF-1042" required />
            <button className="primary-button" disabled={loading}>{loading ? "Checking…" : "Check status"}</button>
          </div>
        </form>
        {error && <div className="message error" role="alert">{error}</div>}
      </div>
      {item && <div className="status-result" aria-live="polite"><ItemCard item={item} showStatus /></div>}
    </section>
  );
}
