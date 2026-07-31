import "./ClarificationModal.css";
import { useState } from "react";

export default function ClarificationModal({ gap, onSubmit, loading }) {
  const fields = gap?.missing_fields || [];
  const [answers, setAnswers] = useState({});
  if (!fields.length) return null;

  const update = (field, value) => setAnswers((prev) => ({ ...prev, [field]: value }));
  const submit = (e) => {
    e.preventDefault();
    onSubmit(answers);
  };

  return <div className="clarify-overlay">
    <form className="clarify-card" onSubmit={submit}>
      <div className="clarify-steam">⌁</div>
      <p className="section-eyebrow">A LITTLE PAUSE AT THE COUNTER</p>
      <h2>Before I brew this...</h2>
      <p className="clarify-intro">I found a few details that would genuinely change the quality of your final prompt.</p>
      <div className="clarify-fields">
        {fields.map((item, i) => {
          const key = item.field || `field_${i}`;
          const type = item.input_type || "text";
          const label = item.question || `What should I know about ${item.field}?`;
          const Tag = type === "textarea" ? "textarea" : "input";
          return <label key={key}>
            <span>{String(i+1).padStart(2,"0")} · {label}</span>
            <Tag type={Tag==="input" ? (type==="number" ? "number" : type==="date" ? "date" : "text") : undefined}
              value={answers[key] || ""}
              onChange={(e)=>update(key,e.target.value)}
              placeholder={`Your answer about ${item.field || "this detail"}...`}
              required
            />
          </label>;
        })}
      </div>
      <div className="clarify-actions"><span>{fields.length} clarification{fields.length>1?"s":""}</span><button disabled={loading}>{loading ? "Continuing..." : "Continue brewing →"}</button></div>
    </form>
  </div>;
}
