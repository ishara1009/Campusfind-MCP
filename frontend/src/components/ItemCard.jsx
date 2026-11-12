function formatDate(value) {
  return new Intl.DateTimeFormat("en-GB", {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}


export default function ItemCard({ item, showStatus = false }) {
  return (
    <article className="item-card">
      <div className="item-card-heading">
        <div>
          <p className="eyebrow">{item.category}</p>
          <h3>{item.item_name}</h3>
        </div>
        {showStatus && (
          <span className={`status-badge ${item.status}`}>
            {item.status === "available" ? "Available" : "Returned"}
          </span>
        )}
      </div>
      <dl className="item-details">
        <div><dt>Color</dt><dd>{item.color}</dd></div>
        <div><dt>Location</dt><dd>{item.found_location}</dd></div>
        <div><dt>Found date</dt><dd>{formatDate(item.found_date)}</dd></div>
        <div><dt>Reference</dt><dd className="reference-code">{item.reference_code}</dd></div>
      </dl>
      {item.description && <p className="item-description">{item.description}</p>}
    </article>
  );
}
