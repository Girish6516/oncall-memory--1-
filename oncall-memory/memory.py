"""
Thin wrapper around Hindsight so the rest of the app never touches the SDK
directly. A fresh client is created on every call (not cached) because
Streamlit re-runs this script on every interaction, and reusing one async
client across re-runs causes "Timeout context manager should be used
inside a task" errors.
"""
import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()
BANK = os.getenv("HINDSIGHT_BANK_ID", "oncall-memory")


def _new_client():
    base_url = os.getenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    api_key = os.getenv("HINDSIGHT_API_KEY")
    if not api_key or "your_" in api_key:
        raise RuntimeError(
            "HINDSIGHT_API_KEY is missing in .env. "
            "Get it from https://ui.hindsight.vectorize.io"
        )
    return Hindsight(base_url=base_url, api_key=api_key)


def retain_incident(inc: dict) -> None:
    """Store one resolved incident, including the OUTCOME of the fix."""
    text = (
        f"INCIDENT {inc['id']} | service: {inc['service']} | date: {inc['date']}\n"
        f"Symptom: {inc['symptom']}\n"
        f"Root cause: {inc['root_cause']}\n"
        f"Fix attempted: {inc['fix']}\n"
        f"Outcome: {inc['outcome']}"
    )
    try:
        _new_client().retain(bank_id=BANK, content=text)
    except Exception as e:
        raise RuntimeError(f"Hindsight retain() failed: {e}") from e


def recall(query: str, limit: int = 10) -> list[str]:
    """Return the most relevant memory texts for an alert."""
    try:
        resp = _new_client().recall(bank_id=BANK, query=query)
    except Exception as e:
        raise RuntimeError(f"Hindsight recall() failed: {e}") from e
    results = getattr(resp, "results", None)
    if results is None:
        results = resp if isinstance(resp, list) else []
    texts = []
    for r in results:
        t = getattr(r, "text", None) or getattr(r, "content", None) or (r if isinstance(r, str) else None)
        if t:
            texts.append(t)
    return texts[:limit]