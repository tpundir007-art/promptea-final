import "./Workflow.css";

const agents = [
  ["Validation","Checking the prompt","✓","#5D7B3D"],
  ["Complexity","Measuring the brew","◈","#A7C7E4"],
  ["Gap Analysis","Finding missing ingredients","⌕","#F6C94D"],
  ["Context","Understanding intent","◌","#F29BB9"],
  ["Technique","Choosing the tools","✦","#F6C94D"],
  ["Strategy","Writing the recipe","♟","#A7C7E4"],
  ["Refiner","Improving the prompt","✧","#F29BB9"],
  ["Critic","Tasting the result","⌕","#E45688"],
  ["Cost Optimizer","Trimming the tokens","◫","#5D7B3D"],
  ["Simulator","Taking a test sip","◇","#A7C7E4"],
  ["Scorecard","Scoring the cup","★","#F6C94D"],
  ["Explainability","Writing tea notes","🫖","#0C6038"],
];

export default function Workflow({ activeStep=0, paused=false }) {
  return <section className="workflow-container">
    <div className="workflow-heading"><span>⌁</span><div><p className="workflow-eyebrow">THE KITCHEN</p><h2>Brewing your prompt</h2><p>Every station has a job.</p></div><span>⌁</span></div>
    <div className="workflow">
      {agents.map(([name,desc,icon,color],i)=>{
        const step=i+1, completed=activeStep>step, active=activeStep===step;
        return <div className="workflow-item" key={name}>
          <div className={`workflow-card ${active?"active":""} ${completed?"completed":""} ${activeStep<step?"waiting":""}`}>
            <div className="workflow-icon" style={{"--agent-color":color}}>{completed?"✓":icon}{active&&<i/>}</div>
            <div><span className="workflow-number">{String(step).padStart(2,"0")}</span><p>{name}</p><small>{completed?"Complete":active?desc:"Waiting"}</small></div>
          </div>
          {i<agents.length-1&&<div className={`workflow-line ${completed?"line-completed":""}`}/>}
        </div>
      })}
    </div>
    <div className="workflow-footer"><span className="brewing-dot"/>{paused?"A detail is needed before the next station.":activeStep>=12?"The cup is ready.":"Steeping your prompt..."}</div>
  </section>;
}
