import "./Simulator.css";

export default function Simulator({ simulator = {} }) {
  if (!simulator || !Object.keys(simulator).length) return null;
  const confidence = Number(simulator.confidence || 0);
  const profile = simulator.execution_profile || {};
  return (
    <section className="simulator-card result-section">
      <div className="section-heading"><span className="section-icon">🧪</span><div><p className="section-eyebrow">BEFORE YOU SERVE</p><h2>Simulator</h2><p>A small test sip of what the optimized prompt is likely to produce.</p></div></div>
      <div className="simulator-grid">
        <div className="prediction"><span>Predicted quality</span><strong>{simulator.predicted_quality || "Unknown"}</strong><div className="confidence"><div><span>Confidence</span><b>{Math.round(confidence*100)}%</b></div><i><em style={{width:`${Math.max(0,Math.min(100,confidence*100))}%`}}/></i></div></div>
        <div className="preview"><span>Output preview</span><p>{simulator.output_preview || "No preview returned."}</p></div>
      </div>
      <div className="simulator-lists">
        {simulator.strengths?.length ? <div><h3>✓ Strengths</h3>{simulator.strengths.map((x,i)=><p key={i}>{x}</p>)}</div>:null}
        {simulator.possible_issues?.length ? <div><h3>⚠ Possible issues</h3>{simulator.possible_issues.map((x,i)=><p key={i}>{x}</p>)}</div>:null}
      </div>
      {simulator.recommendation && <div className="recommendation"><b>Barista recommendation</b><p>{simulator.recommendation}</p></div>}
      {Object.keys(profile).length>0 && <div className="execution-profile"><span>Estimated output tokens: {profile.estimated_tokens ?? "—"}</span><span>Reasoning: {profile.reasoning_level ?? "—"}</span><span>Sections: {Array.isArray(profile.estimated_sections) ? profile.estimated_sections.join(", ") : "—"}</span></div>}
    </section>
  );
}
