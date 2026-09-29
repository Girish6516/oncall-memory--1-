"""
Run this FIRST, before seed.py or the app: python test_connection.py
It checks Groq and Hindsight separately and tells you exactly which one
is misconfigured, instead of a confusing error buried inside Streamlit.
"""
import os, sys
from dotenv import load_dotenv
load_dotenv()

ok = True

print("1) Checking .env file...")
required = ["GROQ_API_KEY", "HINDSIGHT_API_KEY", "HINDSIGHT_BASE_URL"]
for key in required:
    val = os.getenv(key)
    if not val or "your_" in val:
        print(f"   MISSING: {key} is not set in .env")
        ok = False
    else:
        print(f"   OK: {key} is set")

if not ok:
    print("\nFix your .env file first, then run this script again.")
    sys.exit(1)

print("\n2) Testing Groq...")
try:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    r = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        messages=[{"role": "user", "content": "Reply with the single word: OK"}],
        max_tokens=5,
    )
    print("   Groq responded:", r.choices[0].message.content.strip())
except Exception as e:
    print("   GROQ FAILED:", e)
    print("   -> Check GROQ_API_KEY at https://console.groq.com/keys")
    ok = False

print("\n3) Testing Hindsight...")
try:
    from hindsight_client import Hindsight
    hs = Hindsight(base_url=os.getenv("HINDSIGHT_BASE_URL"), api_key=os.getenv("HINDSIGHT_API_KEY"))
    bank = os.getenv("HINDSIGHT_BANK_ID", "oncall-memory")
    hs.retain(bank_id=bank, content="Connection test memory: this is just a test entry.")
    print("   Hindsight retain() succeeded.")
    result = hs.recall(bank_id=bank, query="connection test")
    print("   Hindsight recall() succeeded, returned:", result)
except Exception as e:
    print("   HINDSIGHT FAILED:", e)
    print("   -> Check HINDSIGHT_API_KEY and HINDSIGHT_BASE_URL")
    print("   -> Compare method names against https://hindsight.vectorize.io/ docs")
    print("   -> If retain()/recall() have different argument names in your installed")
    print("      version, run: python -c \"from hindsight_client import Hindsight; help(Hindsight)\"")
    ok = False

print("\n" + ("ALL CHECKS PASSED. Run: python seed.py" if ok else "FIX THE ITEMS ABOVE, then re-run this script."))
