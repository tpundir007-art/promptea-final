import { useState } from "react";
import "./RefinedPrompt.css";

export default function RefinedPrompt({ originalPrompt, refinedPrompt }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    if (!refinedPrompt) return;
    try {
      await navigator.clipboard.writeText(refinedPrompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {}
  };
  return (
    <section className="result-section refined-section">
      <div className="section-heading">
        <span className="section-icon">📝</span>
        <div>
          <p className="section-eyebrow">THE BEFORE & AFTER</p>
          <h2>From rough idea to refined brew</h2>
        </div>
      </div>
      <div className="prompt-book">
        <div className="prompt-side original-side">
          <span className="prompt-number">01</span>
          <span className="prompt-label">Original</span>
          <p>{originalPrompt || "—"}</p>
        </div>
        <div className="prompt-arrow">→</div>
        <div className="prompt-side final-side">
          <div className="final-top">
            <div><span className="prompt-number">02</span><span className="prompt-label">Final Brew</span></div>
            <button onClick={copy} className="copy-button">{copied ? "✓ Copied" : "Copy prompt"}</button>
          </div>
          <p>{refinedPrompt || "No refined prompt was returned."}</p>
        </div>
      </div>
    </section>
  );
}
