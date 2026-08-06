import { createPortal } from "react-dom";
import "./PersonalizeModal.css";

// Keys must exactly match PERSONALIZATION_PRESETS in the backend's
// app.py. If you add/rename a preset here, update it there too.
export const PERSONALIZATION_PRESETS = [
  { key: "examples", label: "Real-world examples", emoji: "🌰" },
  { key: "bullet_points", label: "Bullet points", emoji: "🍡" },
  { key: "step_by_step", label: "Step-by-step", emoji: "🪜" },
  { key: "concise", label: "Concise & to the point", emoji: "⚡" },
];

export const MAX_CUSTOM_PERSONALIZATION_LENGTH = 300;

function PersonalizeModal({
  isOpen,
  onClose,
  selected,
  onToggle,
  customText,
  onCustomTextChange,
}) {
  if (!isOpen) return null;

  return createPortal(
    <div className="modal-overlay" onClick={onClose}>
      <div className="personalize-modal" onClick={(e) => e.stopPropagation()}>
        <h2>Personalize your cup 🎨</h2>
        <p>
          Tell PrompTea how you'd like the final answer delivered. Pick as
          many as you like, or write your own below.
        </p>

        <div className="personalize-grid">
          {PERSONALIZATION_PRESETS.map(({ key, label, emoji }) => {
            const active = selected.includes(key);
            return (
              <button
                type="button"
                key={key}
                className={`personalize-chip ${active ? "active" : ""}`}
                onClick={() => onToggle(key)}
                aria-pressed={active}
              >
                <span className="chip-emoji">{emoji}</span>
                <span>{label}</span>
                {active && <span className="chip-check">✓</span>}
              </button>
            );
          })}
        </div>

        <label className="personalize-other">
          <span>✎ Other (write your own)</span>
          <textarea
            value={customText}
            maxLength={MAX_CUSTOM_PERSONALIZATION_LENGTH}
            placeholder="e.g. explain this assuming I already know Python..."
            onChange={(e) => onCustomTextChange(e.target.value)}
          />
          <small>
            {customText.length}/{MAX_CUSTOM_PERSONALIZATION_LENGTH}
          </small>
        </label>

        <button className="close-btn" onClick={onClose}>
          Done
        </button>
      </div>
    </div>,
    document.body
  );
}

export default PersonalizeModal;