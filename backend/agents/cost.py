import math
import re

from helpers import ask_llm_json, compact
from prompts.cost_prompt import COST_OPTIMIZER_PROMPT


def _estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text or "") / 4))


def _num(value, default=0.0) -> float:
    """LLMs return '35%', '120 tokens', None... never crash on that."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    m = re.search(r"-?\d+(?:\.\d+)?", str(value or ""))
    return float(m.group()) if m else default


def cost_agent(context: dict, optimized_prompt: str, mode: str = "Balanced"):
    user_input = (
        f"Context Package:\n{compact(context)}\n\n"
        f"Optimized Prompt:\n{optimized_prompt}\n\n"
        f"Optimization Mode:\n{mode}\n"
    )
    result = ask_llm_json(COST_OPTIMIZER_PROMPT, user_input)

    result.setdefault("optimization_mode", mode)
    if not str(result.get("optimized_prompt") or "").strip():
        result["optimized_prompt"] = optimized_prompt
    result.setdefault("estimated_token_reduction", 0)
    result.setdefault("quality_preservation", 100)
    if not isinstance(result.get("changes"), list):
        result["changes"] = []

    after = int(_num(result.get("estimated_prompt_tokens")) or _estimate_tokens(result["optimized_prompt"]))
    reduction = _num(result.get("estimated_token_reduction"))
    result["estimated_prompt_tokens"] = after

    before = round(after / (1 - reduction / 100)) if 0 < reduction < 100 else after
    result["estimated_original_tokens"] = max(before, after)
    result["estimated_tokens_saved"] = max(0, result["estimated_original_tokens"] - after)
    return result
