"""Incident agent: recall -> reason -> answer. Memory can be toggled off for the before/after demo."""
import os
from dotenv import load_dotenv
from groq import Groq
import memory

load_dotenv()
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
llm = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM = """You are an on-call incident response assistant for an SRE team.
Given a live alert and (optionally) memories of past incidents, produce:
1. Likely root cause
2. Recommended fix, in order
3. What NOT to try (fixes that failed before on similar incidents)
4. Evidence: cite incident IDs (e.g. INC-102) from memory

Rules:
- Rank fixes by their recorded OUTCOME. Never recommend a fix that FAILED before for the same root cause.
- If no memory is provided, give generic best-practice advice and say you have no team history.
- Be concise: max 180 words. Use short bullets."""


def _chat(messages):
    # Retry once: models on Groq occasionally return malformed or empty output
    last_err = None
    for attempt in range(2):
        try:
            r = llm.chat.completions.create(model=MODEL, messages=messages, temperature=0.2)
            out = r.choices[0].message.content
            if out and out.strip():
                return out
        except Exception as e:
            last_err = e
    return f"LLM error: {last_err}" if last_err else "LLM returned an empty answer. Try again."


def respond(alert: str, use_memory: bool = True):
    """Returns (answer, recalled_memories, memory_error)."""
    memories, mem_error = [], None
    if use_memory:
        try:
            memories = memory.recall(alert)
        except Exception as e:
            mem_error = str(e)

    user = f"LIVE ALERT:\n{alert}\n\n"
    if memories:
        user += "MEMORIES OF PAST INCIDENTS:\n" + "\n---\n".join(memories)
    else:
        user += "MEMORIES: none available."
    answer = _chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}])
    return answer, memories, mem_error
