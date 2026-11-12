import { useState } from "react";

import { createReport } from "../api/itemsApi";


const initialForm = {
  item_name: "",
  category: "",
  color: "",
  found_location: "",
  found_date: "",
  description: "",
};


export default function ReportItemPage() {
  const [form, setForm] = useState(initialForm);
  const [pending, setPending] = useState(false);
  const [referenceCode, setReferenceCode] = useState("");
  const [error, setError] = useState("");

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (pending) return;
    setPending(true);
    setError("");
    setReferenceCode("");
    try {
      const result = await createReport(form);
      setReferenceCode(result.reference_code);
      setForm(initialForm);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="page-layout">
      <div className="page-intro">
        <p className="eyebrow">Help it find its owner</p>
        <h1>Report a found item.</h1>
        <p>Share the details you know. We will create a reference code so you can check the report later.</p>
        <div className="tip-card"><span>01</span><p>Use a clear item name and the exact campus location.</p></div>
        <div className="tip-card"><span>02</span><p>Keep the reference code shown after you submit.</p></div>
      </div>
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>Item name<input name="item_name" value={form.item_name} onChange={updateField} required maxLength="150" placeholder="Water bottle" /></label>
            <label>Category<input name="category" value={form.category} onChange={updateField} required maxLength="80" placeholder="Personal item" /></label>
            <label>Color<input name="color" value={form.color} onChange={updateField} required maxLength="80" placeholder="Blue" /></label>
            <label>Found location<input name="found_location" value={form.found_location} onChange={updateField} required maxLength="150" placeholder="Cafeteria" /></label>
            <label className="full-width">Found date<input type="date" name="found_date" value={form.found_date} onChange={updateField} required /></label>
            <label className="full-width">Description <span className="optional">Optional</span><textarea name="description" value={form.description} onChange={updateField} maxLength="2000" rows="4" placeholder="Where exactly did you find it?" /></label>
            <button className="primary-button form-action" disabled={pending}>{pending ? "Saving report…" : "Create report"}</button>
          </div>
        </form>
        {error && <div className="message error" role="alert">{error}</div>}
        {referenceCode && <div className="message success" role="status"><p>Report saved successfully</p><strong>{referenceCode}</strong><span>Keep this code to check the report status.</span></div>}
      </div>
    </section>
  );
}
