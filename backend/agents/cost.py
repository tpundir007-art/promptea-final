import json
import math

from helpers import ask_llm_json
from prompts.cost_prompt import COST_OPTIMIZER_PROMPT


def _estimate_tokens(text: str) -> int:
    # Deliberately labelled as an estimate. No tokenizer dependency is added.
    return max(1, math.ceil(len(text or "") / 4))


def cost_agent(context: dict, optimized_prompt: str, mode: str = "Balanced"):
    user_input = f"""
Context Package:
{json.dumps(context, indent=2)}

Optimized Prompt:
{optimized_prompt}

Optimization Mode:
{mode}
"""

    result = ask_llm_json(
        COST_OPTIMIZER_PROMPT,
        user_input,
    ) or {}

    result.setdefault("optimization_mode", mode)
    result.setdefault("optimized_prompt", optimized_prompt)
    result.setdefault("estimated_prompt_tokens", _estimate_tokens(optimized_prompt))
    result.setdefault("estimated_token_reduction", 0)
    result.setdefault("quality_preservation", 100)
    result.setdefault("changes", [])

    after = int(result.get("estimated_prompt_tokens") or 0)
    reduction = float(result.get("estimated_token_reduction") or 0)

    if reduction > 0 and reduction < 100:
        before = round(after / (1 - reduction / 100))
    else:
        before = _estimate_tokens(optimized_prompt)

    result["estimated_original_tokens"] = max(before, after)
    result["estimated_tokens_saved"] = max(
        0, result["estimated_original_tokens"] - after
    )

    return result
