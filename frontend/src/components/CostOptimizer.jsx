import "./CostOptimizer.css";

function CostOptimizer({ cost }) {
  if (!cost) return null;

  const reduction = Number(cost.estimated_token_reduction || 0);
  const estimatedTokens = Number(cost.estimated_prompt_tokens || 0);
  const originalTokens =
    reduction > 0
      ? Math.round(estimatedTokens / (1 - reduction / 100))
      : estimatedTokens;

  const savedTokens = Math.max(originalTokens - estimatedTokens, 0);

  return (
    <section className="cost-card result-section">
      <div className="section-heading">
        <span className="section-icon">💰</span>
        <div>
          <p className="eyebrow">COST OPTIMIZATION</p>
          <h2>Efficient Brewing</h2>
        </div>
      </div>

      <div className="cost-stats">
        <div className="cost-stat">
          <span>Before</span>
          <strong>~{originalTokens}</strong>
          <small>tokens</small>
        </div>

        <div className="cost-arrow">→</div>

        <div className="cost-stat highlight">
          <span>Optimized</span>
          <strong>{estimatedTokens}</strong>
          <small>tokens</small>
        </div>

        <div className="cost-stat saved">
          <span>Saved</span>
          <strong>{savedTokens}</strong>
          <small>tokens</small>
        </div>
      </div>

      <div className="cost-reduction">
        <div className="cost-reduction-header">
          <span>Token reduction </span>
          <strong>{reduction.toFixed(1)}%</strong>
        </div>

        <div className="cost-progress">
          <div
            className="cost-progress-fill"
            style={{ width: `${Math.min(reduction, 100)}%` }}
          />
        </div>
      </div>

      {cost.quality_preservation !== undefined && (
        <div className="cost-quality">
          <span>Quality preserved </span>
          <strong>{cost.quality_preservation}%</strong>
        </div>
      )}

      {Array.isArray(cost.changes) && cost.changes.length > 0 && (
        <div className="cost-changes">
          <h3>What was optimized</h3>

          <ul>
            {cost.changes.map((change, index) => (
              <li key={index}>{change}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

export default CostOptimizer;