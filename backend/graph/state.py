from typing import TypedDict, Any


class PromptState(TypedDict):
    # ==========================
    # User Input
    # ==========================
    original_prompt: str
    level: str

    # ==========================
    # Validation
    # ==========================
    validation: dict[str, Any]

    # ==========================
    # Analysis Agents
    # ==========================
    complexity: dict[str, Any]
    gap: dict[str, Any]
    answers: dict[str, Any]
    context: dict[str, Any]

    # ==========================
    # Prompt Engineering
    # ==========================
    selected_techniques: list[str]
    technique_reasoning: str

    strategy: dict[str, Any]

    draft_prompt: str
    refined_prompt: str

    # ==========================
    # Critic Loop
    # ==========================
    critique: dict[str, Any]
    retry_count: int

    # ==========================
    # Optimization
    # ==========================
    cost: dict[str, Any]
    simulator: dict[str, Any]

    # ==========================
    # Final Output
    # ==========================
    score: dict[str, Any]
    explanation: dict[str, Any]