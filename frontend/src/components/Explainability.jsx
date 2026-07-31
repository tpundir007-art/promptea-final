import "./Explainability.css";

export default function Explainability({ explanation = {} }) {
  if (!explanation || !Object.keys(explanation).length) return null;
  const techniques = explanation.techniques_used || [];
  return <section className="tea-notes result-section">
    <div className="tea-paper">
      <div className="tea-header"><span>🫖</span><div><p className="section-eyebrow">TEA NOTES</p><h2>Here's how your prompt was refined.</h2></div></div>
      {explanation.summary && <div className="tea-block"><h3>🌸 Summary</h3><p>{explanation.summary}</p></div>}
      {explanation.major_improvements?.length ? <div className="tea-block"><h3>🌸 Major Improvements</h3><ul>{explanation.major_improvements.map((x,i)=><li key={i}>{x}</li>)}</ul></div>:null}
      {techniques.length ? <div className="tea-block"><h3>🎯 Techniques Used</h3><div className="tea-techniques">{techniques.map((t,i)=><div key={i}><strong>{t.technique || t.name}</strong><span>{t.purpose || t.description || ""}</span></div>)}</div></div>:null}
      {explanation.overall_assessment && <div className="tea-block tea-final"><h3>☕ Barista's Note</h3><p>{explanation.overall_assessment}</p></div>}
    </div>
  </section>;
}
