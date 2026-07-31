import "./AnalysisCards.css";

const FIELD_LABELS = {
  complexity_level: "Complexity",
  complexity_score: "Complexity score",
  confidence: "Confidence",
  task_type: "Task type",
  reasoning_required: "Reasoning",
  summary: "Summary",
  status: "Status",
  message: "Message",
  reason: "Reason",
  intent: "Intent",
  goal: "Goal",
};

function pretty(value) {
  if (value === null || value === undefined || value === "") return null;
  if (Array.isArray(value)) return value.length ? value.join(" • ") : null;
  if (typeof value === "object") return null;
  return String(value);
}

function DiagnosisCard({ icon, title, data, tone }) {
  const object = data && typeof data === "object" ? data : {};
  const entries = Object.entries(object)
    .filter(([key, value]) => key !== "continue_pipeline" && pretty(value))
    .slice(0, 5);

  return (
    <article className={`diagnosis-card ${tone || ""}`}>
      <div className="diagnosis-card-top">
        <span className="diagnosis-icon">{icon}</span>
        <div>
          <span className="diagnosis-label">{title}</span>
          <h4>{pretty(object.summary) || pretty(object.message) || "Analysis complete"}</h4>
        </div>
      </div>
      <div className="diagnosis-details">
        {entries.map(([key, value]) => (
          <div className="diagnosis-detail" key={key}>
            <span>{FIELD_LABELS[key] || key.replaceAll("_", " ")}</span>
            <strong>{pretty(value)}</strong>
          </div>
        ))}
      </div>
    </article>
  );
}

export default function AnalysisCards({ validation, complexity, gap, context }) {
  const missing = gap?.missing_fields || [];
  return (
    <section className="analysis-section result-section">
      <div className="section-heading">
        <span className="section-icon">🔍</span>
        <div>
          <p className="section-eyebrow">PROMPT DIAGNOSIS</p>
          <h2>What the baristas found</h2>
          <p>Four lenses before the actual brewing begins.</p>
        </div>
      </div>

      <div className="diagnosis-grid">
        <DiagnosisCard icon="✓" title="Validation" data={validation} tone="green" />
        <DiagnosisCard icon="◈" title="Complexity" data={complexity} tone="blue" />
        <DiagnosisCard
          icon="⌕"
          title="Missing ingredients"
          data={{
            summary: missing.length
              ? `${missing.length} detail${missing.length > 1 ? "s" : ""} needed`
              : "No major gaps detected.",
            ...((missing.length && { missing: missing.map((item) => item.field || item.question) }) || {}),
          }}
          tone="gold"
        />
        <DiagnosisCard icon="◌" title="Context" data={context} tone="pink" />
      </div>
    </section>
  );
}
