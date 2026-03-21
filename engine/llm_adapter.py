import os
import json
from typing import Dict, Any, Optional


def _offline_mutate(code: str) -> str:
    # safe fallback if no LLM configured
    lines = code.splitlines()
    if not lines:
        return code

    # simple, deterministic-ish tweaks
    out = []
    for ln in lines:
        if "print(" in ln:
            out.append(ln.replace("print(", "print('llm_mut:', "))
        else:
            out.append(ln)
    if not any("llm_mut" in l for l in out):
        out.append("# llm_mutation_applied")
    return "\n".join(out)


def _openai_chat(prompt: str) -> Optional[str]:
    """
    Optional: set OPENAI_API_KEY to enable.
    Returns code string or None on failure.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI  # requires `openai` package installed
        client = OpenAI(api_key=api_key)

        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": "You rewrite Python code safely. Return ONLY valid Python code."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        content = resp.choices[0].message.content
        if content and isinstance(content, str):
            return content.strip()
    except Exception:
        return None

    return None


def llm_mutate_code(original_code: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Try LLM → fallback to offline mutation.
    """
    ctx = json.dumps(context or {}, indent=2)
    prompt = f"""Improve or slightly mutate this Python function.
Constraints:
- Keep it valid Python
- Preserve the function signature
- Avoid imports unless necessary
- Keep side-effects minimal

Context:
{ctx}

Code:
{original_code}
"""
    out = _openai_chat(prompt)
    if out:
        return out

    return _offline_mutate(original_code)
