
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./History.css";

function groupByDate(brews) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const oneWeekAgo = new Date(today);
  oneWeekAgo.setDate(today.getDate() - 7);

  const groups = {
    Today: [],
    "This week": [],
    Earlier: [],
  };

  brews.forEach((brew) => {
    const brewDate = new Date(brew.date);
    brewDate.setHours(0, 0, 0, 0);

    if (brewDate.getTime() === today.getTime()) {
      groups.Today.push(brew);
    } else if (brewDate > oneWeekAgo) {
      groups["This week"].push(brew);
    } else {
      groups.Earlier.push(brew);
    }
  });

  return groups;
}

function History() {
  const [pastBrews, setPastBrews] = useState([]);

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("brewHistory") || "[]");
      setPastBrews(Array.isArray(saved) ? saved : []);
    } catch {
      setPastBrews([]);
    }
  }, []);

  const groups = groupByDate(pastBrews);

  return (
    <div className="history-page">
      <h1>Your Brew History</h1>

      {pastBrews.length === 0 ? (
        <div className="empty-state">
          <p>No prompts brewed yet.</p>

          <Link to="/brew">
            <button className="empty-btn">
              Brew your first prompt
            </button>
          </Link>
        </div>
      ) : (
        Object.entries(groups).map(([label, brews]) =>
          brews.length === 0 ? null : (
            <div key={label} className="history-group">
              <p className="group-label">{label.toUpperCase()}</p>

              <div className="history-list">
                {brews.map((brew) => (
                  <div key={brew.id} className="history-card">
                    <p className="history-prompt">
                      "{brew.originalPrompt}"
                    </p>

                    <div className="history-meta">
                      <span>
                        Score: {brew.score?.overall_score ?? "—"}/10
                      </span>

                      <span>{brew.date}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        )
      )}
    </div>
  );
}

export default History;

