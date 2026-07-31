import { useEffect, useState } from "react";
import "./Scorecard.css";

const labels = {
  clarity: "Clarity",
  specificity: "Specificity",
  structure: "Structure",
  intent_preservation: "Intent Preservation",
  hallucination_safety: "Hallucination Safety",
  strategy_adherence: "Strategy Adherence",
  readiness: "Readiness",
};

function Bar({ value }) {
  const [width, setWidth] = useState(0);
  useEffect(() => { const t=setTimeout(()=>setWidth(Math.max(0,Math.min(100,Number(value||0)*10))),80); return ()=>clearTimeout(t); },[value]);
  return <div className="score-bar"><i style={{width:`${width}%`}}/></div>;
}

export default function Scorecard({ score = {} }) {
  if (!score || !Object.keys(score).length) return null;
  const overall = Number(score.overall_score || 0);
  const metrics = Object.entries(labels).filter(([key]) => score[key] && typeof score[key] === "object");
  return <section className="scorecard-card result-section">
    <div className="section-heading"><span className="section-icon">📊</span><div><p className="section-eyebrow">FINAL TASTING</p><h2>Prompt score</h2><p>{score.summary || "A structured evaluation of the final brew."}</p></div><div className="overall-number"><strong>{overall.toFixed(1)}</strong><small>/ 10</small></div></div>
    <div className="score-metrics">{metrics.map(([key,label])=>{const val=Number(score[key].score||0);return <div className="score-metric" key={key}><div><span>{label}</span><b>{Math.round(val*10)}%</b></div><Bar value={val}/><p>{score[key].reason || ""}</p></div>})}</div>
    {!!score.strengths?.length && <div className="score-columns"><div><h3>What worked</h3>{score.strengths.map((x,i)=><p key={i}>✓ {x}</p>)}</div>{score.improvements?.length?<div><h3>Could be stronger</h3>{score.improvements.map((x,i)=><p key={i}>→ {x}</p>)}</div>:null}</div>}
  </section>;
}
