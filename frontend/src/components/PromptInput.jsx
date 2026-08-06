import { useState } from "react";
import "./PromptInput.css";
import PersonalizeModal from "./PersonalizeModal";

function PromptInput({ onSubmit, onSkillClick, loading = false }) {
  const [prompt, setPrompt] = useState("");
  const [personalizeOpen, setPersonalizeOpen] = useState(false);
  const [presets, setPresets] = useState([]);
  const [customText, setCustomText] = useState("");

  const togglePreset = (key) => {
    setPresets((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  };

  const personalizeCount = presets.length + (customText.trim() ? 1 : 0);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!prompt.trim()) return;

    onSubmit(prompt, {
      presets,
      custom: customText.trim(),
    });
  };

  return (
    <div className="prompt-container">
      <div className="prompt-header">
        <h2>Brew Your Prompt ☕</h2>
        <p>Turn ordinary prompts into extraordinary ones.</p>
      </div>

      <form onSubmit={handleSubmit}>
        <textarea
          placeholder="What's brewing in your mind today?"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          maxLength={3000}
        />

        <div className="prompt-footer">
          <span>{prompt.length}/3000</span>

          <div className="buttons">
            <button
              type="button"
              className="skill-btn"
              onClick={onSkillClick}
            >
              🍃 Choose Skill
            </button>

            <button
              type="button"
              className={`skill-btn ${personalizeCount ? "has-selection" : ""}`}
              onClick={() => setPersonalizeOpen(true)}
            >
              🎨 Personalize{personalizeCount ? ` (${personalizeCount})` : ""}
            </button>

            <button
              type="submit"
              className="brew-btn"
              disabled={loading}
            >
              {loading ? "Brewing..." : "☕ Brew Prompt"}
            </button>
          </div>
        </div>
      </form>

      <PersonalizeModal
        isOpen={personalizeOpen}
        onClose={() => setPersonalizeOpen(false)}
        selected={presets}
        onToggle={togglePreset}
        customText={customText}
        onCustomTextChange={setCustomText}
      />
    </div>
  );
}

export default PromptInput;