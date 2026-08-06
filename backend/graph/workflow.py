from langgraph.graph import StateGraph, END

from graph.state import PromptState
from agents.validator import validation_agent
from agents.complex import complexity_agent
from agents.gap import gap_agent
from agents.context import context_agent
from agents.technique import technique_agent
from agents.strategy import strategy_agent
from agents.refiner import refiner_agent
from agents.critic import critic_agent
from agents.cost import cost_agent
from agents.simulator import simulator_agent
from agents.scorecard import scorecard_agent
from agents.explainability import explainability_agent


def validation_node(state: PromptState):
    state["validation"] = validation_agent(state)
    return state


def complexity_node(state: PromptState):
    state["complexity"] = complexity_agent(state["original_prompt"])
    return state


def gap_node(state: PromptState):
    state["gap"] = gap_agent(state["original_prompt"])
    return state


def context_node(state: PromptState):
    state["context"] = context_agent(
        state["original_prompt"],
        state["complexity"],
        state["gap"],
        state.get("answers", {}),
        state.get("level", "Intermediate"),
        state.get("personalization", ""),
    )
    return state


def technique_node(state: PromptState):
    result = technique_agent(state["original_prompt"]) or {}
    state["selected_techniques"] = result.get("selected_techniques", [])
    state["technique_reasoning"] = result.get("technique_reasoning", "")
    return state


def strategy_node(state: PromptState):
    return strategy_agent(state)


def refiner_node(state: PromptState):
    return refiner_agent(state)


def critic_node(state: PromptState):
    return critic_agent(state)


def critic_router(state: PromptState):
    critique = state.get("critique") or {}
    decision = str(critique.get("decision", "accept")).lower()

    if decision == "refine" and state.get("retry_count", 0) < 3:
        return "Retry"

    return "Cost"


def retry_node(state: PromptState):
    state["retry_count"] = state.get("retry_count", 0) + 1
    return state


def cost_node(state: PromptState):
    complexity = str(
        state.get("complexity", {}).get("complexity_level")
        or state.get("complexity", {}).get("level")
        or "Medium"
    )

    if complexity.lower() == "simple":
        mode = "Token Efficient"
    elif complexity.lower() == "complex":
        mode = "Maximum Quality"
    else:
        mode = "Balanced"

    state["cost"] = cost_agent(
        state["context"],
        state["refined_prompt"],
        mode,
    )
    return state


def simulator_node(state: PromptState):
    state["simulator"] = simulator_agent(
        state["original_prompt"],
        state["context"],
        state["cost"].get("optimized_prompt", state["refined_prompt"]),
    )
    return state


def scorecard_node(state: PromptState):
    return scorecard_agent(state)


def explainability_node(state: PromptState):
    return explainability_agent(state)


def validation_router(state: PromptState):
    if not state["validation"].get("continue_pipeline", True):
        return "END"
    return "Complexity"


def build_pre_gap_workflow():
    builder = StateGraph(PromptState)
    builder.add_node("Validation", validation_node)
    builder.add_node("Complexity", complexity_node)
    builder.add_node("Gap", gap_node)

    builder.set_entry_point("Validation")
    builder.add_conditional_edges(
        "Validation",
        validation_router,
        {"Complexity": "Complexity", "END": END},
    )
    builder.add_edge("Complexity", "Gap")
    builder.add_edge("Gap", END)
    return builder.compile()


def build_post_gap_workflow():
    builder = StateGraph(PromptState)

    builder.add_node("Context", context_node)
    builder.add_node("Technique", technique_node)
    builder.add_node("Strategy", strategy_node)
    builder.add_node("Refiner", refiner_node)
    builder.add_node("Critic", critic_node)
    builder.add_node("Retry", retry_node)
    builder.add_node("Cost", cost_node)
    builder.add_node("Simulator", simulator_node)
    builder.add_node("Scorecard", scorecard_node)
    builder.add_node("Explainability", explainability_node)

    builder.set_entry_point("Context")
    builder.add_edge("Context", "Technique")
    builder.add_edge("Technique", "Strategy")
    builder.add_edge("Strategy", "Refiner")
    builder.add_edge("Refiner", "Critic")
    builder.add_conditional_edges(
        "Critic",
        critic_router,
        {"Retry": "Retry", "Cost": "Cost"},
    )
    builder.add_edge("Retry", "Refiner")
    builder.add_edge("Cost", "Simulator")
    builder.add_edge("Simulator", "Scorecard")
    builder.add_edge("Scorecard", "Explainability")
    builder.add_edge("Explainability", END)

    return builder.compile()


pre_gap_workflow = build_pre_gap_workflow()
post_gap_workflow = build_post_gap_workflow()

# Kept for compatibility with any existing imports.
workflow = post_gap_workflow
