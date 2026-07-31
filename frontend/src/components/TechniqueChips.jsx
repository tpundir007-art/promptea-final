import { useState } from "react";
import "./TechniqueChips.css";

export default function TechniqueChips({ techniques = [], reasoning = "" }) {
  const [open, setOpen] = useState(null);
  if (!techniques?.length) return null;
  const reasonMap = typeof reasoning === "object" ? reasoning : {};
  return <section className="technique-section result-section">
    <div className="section-heading"><span className="section-icon">🎯</span><div><p className="section-eyebrow">BREWING TECHNIQUES</p><h2>The ingredients we chose</h2><p>Hover or tap a chip to see why it belongs in this brew.</p></div></div>
    <div className="technique-chips">{techniques.map((tech,i)=>{const name=typeof tech==="string"?tech:(tech?.technique||tech?.name||"Technique");const detail=typeof tech==="object"?tech?.purpose||tech?.reason||"":(reasonMap[name]||"A prompt-engineering technique selected for this task.");return <div className="technique-wrap" key={`${name}-${i}`} onMouseEnter={()=>setOpen(i)} onMouseLeave={()=>setOpen(null)}><button type="button" className="technique-chip" onClick={()=>setOpen(open===i?null:i)}>✦ {name}</button>{open===i&&<div className="technique-popover"><strong>{name}</strong><p>{detail}</p></div>}</div>})}</div>
  </section>;
}
