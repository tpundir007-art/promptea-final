import { useEffect, useRef, useState } from "react";
import "./Brew.css";
import PromptInput from "../components/PromptInput";
import Workflow from "../components/Workflow";
import AnalysisCards from "../components/AnalysisCards";
import TechniqueChips from "../components/TechniqueChips";
import RefinedPrompt from "../components/RefinedPrompt";
import Scorecard from "../components/Scorecard";
import Explainability from "../components/Explainability";
import CostOptimizer from "../components/CostOptimizer";
import Simulator from "../components/Simulator";
import SkillModal from "../components/SkillModal";
import ClarificationModal from "../components/ClarificationModal";

const API = "http://127.0.0.1:5000";
const TOTAL_STEPS = 12;

const obj = (v) => {
  if (!v) return {};
  if (typeof v === "object") return v;
  try { return JSON.parse(v); } catch { return {}; }
};

function errorMessage(response, data) {
  if (data?.error) return data.error;
  if (!response.ok) return `The brewing service returned ${response.status}.`;
  return "The brewing service returned an unexpected response.";
}

export default function Brew() {
  const [level,setLevel]=useState("Novice");
  const [loading,setLoading]=useState(false);
  const [activeStep,setActiveStep]=useState(0);
  const [result,setResult]=useState(null);
  const [pending,setPending]=useState(null);
  const [selectedSkill,setSelectedSkill]=useState("");
  const [skillOpen,setSkillOpen]=useState(false);
  const [error,setError]=useState("");
  const [sound,setSound]=useState(true);
  const timer=useRef(null);

  const stop=()=>{if(timer.current){clearInterval(timer.current);timer.current=null;}};
  useEffect(()=>()=>stop(),[]);

  const playCupSound=()=>{
    if(!sound) return;
    try{
      const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
      const c=new AC(),o=c.createOscillator(),g=c.createGain();
      o.type="sine";o.frequency.setValueAtTime(523.25,c.currentTime);o.frequency.exponentialRampToValueAtTime(783.99,c.currentTime+.18);
      g.gain.setValueAtTime(.0001,c.currentTime);g.gain.exponentialRampToValueAtTime(.06,c.currentTime+.03);g.gain.exponentialRampToValueAtTime(.0001,c.currentTime+.3);
      o.connect(g);g.connect(c.destination);o.start();o.stop(c.currentTime+.3);
    }catch{}
  };

  const animate=(until=TOTAL_STEPS)=>{
    stop();let n=1;setActiveStep(1);
    timer.current=setInterval(()=>{n+=1;if(n>=until){stop();setActiveStep(until);return;}setActiveStep(n);},420);
  };

  const normalize=(data,promptText)=>{
    return {
      id:Date.now(),originalPrompt:promptText,level,skill:selectedSkill,
      validation:obj(data.validation),complexity:obj(data.complexity),gap:obj(data.gap),answers:data.answers||{},
      context:obj(data.context),selectedTechniques:Array.isArray(data.selected_techniques)?data.selected_techniques:[],
      techniqueReasoning:obj(data.technique_reasoning) || data.technique_reasoning || "",
      strategy:obj(data.strategy),draftPrompt:data.draft_prompt||"",refinedPrompt:data.refined_prompt||data.draft_prompt||"",
      critique:obj(data.critique),retryCount:Number(data.retry_count??data.iterations??0),
      cost:obj(data.cost),simulator:obj(data.simulator),score:obj(data.score),explanation:obj(data.explanation),
      date:new Date().toISOString().split("T")[0],createdAt:new Date().toISOString()
    };
  };

  const saveHistory=(item)=>{
    try{
      const old=JSON.parse(localStorage.getItem("brewHistory")||"[]");
      localStorage.setItem("brewHistory",JSON.stringify([item,...old]));
    }catch{}
  };

  const callGenerate=async(promptText)=>{
    const response=await fetch(`${API}/generate`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt:promptText.trim(),level})});
    const type=response.headers.get("content-type")||"";
    const data=type.includes("application/json")?await response.json():{error:"The brewing service returned a webpage instead of JSON. It may be waking up or temporarily unavailable."};
    if(!response.ok)throw new Error(errorMessage(response,data));
    return data;
  };

  const handleBrew=async(promptText)=>{
    if(!promptText?.trim()||loading)return;
    setLoading(true);setError("");setResult(null);setPending(null);animate(3);
    try{
      const data=await callGenerate(promptText);
      if(data.needs_clarification){
        stop();setActiveStep(3);setPending({gap:data.gap,state:data.pending_state,prompt:promptText});
        setLoading(false);return;
      }
      if(data.status==="complete"){
        stop();setActiveStep(TOTAL_STEPS);
        const item=normalize(data,promptText.trim());setResult(item);saveHistory(item);playCupSound();
      }else if(data.validation?.continue_pipeline===false){
        stop();setActiveStep(1);setResult(normalize(data,promptText.trim()));
      }else throw new Error(data.error||"PrompTea couldn't finish this brew.");
    }catch(e){stop();setActiveStep(0);setError(e.message||"The kettle went a little cold.");}
    finally{setLoading(false);}
  };

  const handleAnswers=async(answers)=>{
    if(!pending?.state)return;
    setLoading(true);setError("");setPending(null);animate(4);
    try{
      const response=await fetch(`${API}/continue`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({state:pending.state,answers})});
      const type=response.headers.get("content-type")||"";
      const data=type.includes("application/json")?await response.json():{error:"The continuation service returned an unexpected response."};
      if(!response.ok)throw new Error(errorMessage(response,data));
      stop();setActiveStep(TOTAL_STEPS);
      const item=normalize(data,pending.prompt);setResult(item);saveHistory(item);playCupSound();
    }catch(e){setError(e.message||"I couldn't continue the brew.");}
    finally{setLoading(false);}
  };

  const retry=()=>{if(result?.originalPrompt)handleBrew(result.originalPrompt);};

  return <main className="brew-page">
    <section className="brew-hero">
      <div className="hero-sparkles"><span>✦</span><span>⌁</span><span>✦</span></div>
      <p className="brew-kicker">THE PROMPTEA CAFÉ</p>
      <h1>Brew something brilliant.</h1>
      <p>Bring your rough idea to the counter.<br/>We'll steep it into a prompt worth using.</p>
    </section>

    <section className="brew-counter">
      <div className="brew-level">
        <div><label htmlFor="level">🌱 Brewing level</label><span>{selectedSkill?`🍃 ${selectedSkill}`:"Choose your tea"}</span></div>
        <select id="level" value={level} onChange={e=>setLevel(e.target.value)} disabled={loading}>
          <option>Novice</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option>
        </select>
      </div>
      <PromptInput onSubmit={handleBrew} onSkillClick={()=>setSkillOpen(true)} loading={loading}/>
      {error&&<div className="brew-error"><span>☕</span><div><strong>The kettle went a little cold.</strong><p>{error}</p></div><button onClick={()=>setError("")}>×</button></div>}
    </section>

    {(loading||result)&&<section className="workflow-shell">
      <div className="workflow-status"><span>{loading?"🫖 PrompTea is brewing...":"✓ Brewing complete"}</span><button onClick={()=>setSound(v=>!v)}>{sound?"🔊":"🔇"}</button></div>
      <Workflow activeStep={activeStep} paused={!!pending}/>
    </section>}

    {result&&<section className="results-wrap">
      <div className="results-hero">
        <div><p className="results-kicker">YOUR CUP IS READY</p><h2>Beautifully brewed. ✨</h2><p>Everything PrompTea discovered, changed and refined — in one place.</p></div>
        <div className="brew-score"><strong>{Number(result.score?.overall_score||0).toFixed(1)}</strong><span>/ 10</span></div>
      </div>

      {result.validation?.continue_pipeline===false&&<div className="notice-card"><strong>PrompTea stopped at validation.</strong><p>{result.validation.message||result.validation.reason||"This input needs a different kind of brew."}</p><button onClick={retry}>Try another prompt</button></div>}

      {result.validation?.continue_pipeline!==false&&<>
        <RefinedPrompt originalPrompt={result.originalPrompt} refinedPrompt={result.refinedPrompt}/>
        <AnalysisCards validation={result.validation} complexity={result.complexity} gap={result.gap} context={result.context}/>
        <TechniqueChips techniques={result.selectedTechniques} reasoning={result.techniqueReasoning}/>
        <section className="result-section strategy-section">
          <div className="section-heading"><span className="section-icon">🧠</span><div><p className="section-eyebrow">BREWING STRATEGY</p><h2>The recipe behind the cup</h2></div></div>
          {result.strategy?.summary&&<p className="strategy-summary">{result.strategy.summary}</p>}
          <div className="recipe-steps">{(result.strategy?.steps||result.strategy?.recipe||result.strategy?.instructions||[]).map((step,i)=><article key={i}><span>{String(step.order||i+1).padStart(2,"0")}</span><div><strong>{step.technique||step.name||"Step"}</strong><p>{step.instruction||step.description||step.purpose||String(step)}</p></div></article>)}</div>
          {result.strategy?.weaknesses?.length&&<div className="weaknesses"><b>What needed attention</b>{result.strategy.weaknesses.map((x,i)=><span key={i}>• {x}</span>)}</div>}
        </section>

        <section className="result-section critic-section">
          <div className="section-heading"><span className="section-icon">🔍</span><div><p className="section-eyebrow">QUALITY CHECK</p><h2>The Critic tasted the brew</h2></div></div>
          <div className="critic-grid">
            <div className="critic-score"><span>Critic score</span><strong>{result.critique?.score??"—"}</strong><small>/ 100</small></div>
            <div><span className={`decision ${String(result.critique?.decision).toLowerCase()}`}>{String(result.critique?.decision||"reviewed").toUpperCase()}</span><p className="critic-feedback">{result.critique?.feedback||"The critic completed its review."}</p>{result.critique?.missing?.length?<div className="missing-chips">{result.critique.missing.map((x,i)=><span key={i}>{x}</span>)}</div>:<p className="no-missing">✓ No missing components reported</p>}</div>
          </div>
          <div className="loop-track"><span>01 Draft</span><i>→</i><span>02 Critic</span>{result.retryCount>0&&<><i>→</i><span>03 Refiner × {result.retryCount}</span><i>→</i><span>04 Critic</span></>}<i>→</i><span>✓ Accepted</span></div>
        </section>

        <Scorecard score={result.score}/>
        <CostOptimizer cost={result.cost}/>
        <Simulator simulator={result.simulator}/>
        <Explainability explanation={result.explanation}/>
      </>}
    </section>}

    <SkillModal isOpen={skillOpen} onClose={()=>setSkillOpen(false)} onSelect={setSelectedSkill}/>
    {pending&&<ClarificationModal gap={pending.gap} onSubmit={handleAnswers} loading={loading}/>}
  </main>;
}
