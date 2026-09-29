import datetime as dt
import streamlit as st
import agent, memory

st.set_page_config(page_title="On-Call Memory", page_icon="🚨", layout="wide")
st.title("🚨 On-Call Memory")
st.caption("An incident-response agent that remembers what actually fixed things, powered by Hindsight.")

for k, v in {"answer": None, "mems": [], "mem_error": None, "count": 110}.items():
    st.session_state.setdefault(k, v)
if "alert_box" not in st.session_state:
    st.session_state["alert_box"] = ""

with st.sidebar:
    use_mem = st.toggle("Use Hindsight memory", value=True)
    st.caption("Turn OFF to show the generic 'before' behavior in your demo.")
    st.markdown("**Try these alerts**")
    demos = {
        "Payments pool exhaustion": "payments-service: 5xx spike and 'connection pool exhausted' errors starting 10 minutes after Friday deploy. Checkout latency 15s.",
        "Email queue backlog": "notifications-worker: queue depth 1.5M and growing, emails delayed 30+ minutes, SMTP 421 throttling responses.",
        "Login failures": "auth-service: about 12% of logins fail with 'JWT signature invalid' after secret rotation.",
    }
    for label, text in demos.items():
        if st.button(label, use_container_width=True):
            st.session_state["alert_box"] = text

alert = st.text_area("Paste the live alert / symptoms", key="alert_box", height=110)

if st.button("Diagnose", type="primary") and alert.strip():
    with st.spinner("Recalling past incidents..." if use_mem else "Thinking..."):
        ans, mems, mem_err = agent.respond(alert, use_memory=use_mem)
    st.session_state.update(answer=ans, mems=mems, mem_error=mem_err)

if st.session_state.mem_error:
    st.error(f"Hindsight memory unavailable, showing generic answer instead: {st.session_state.mem_error}")

if st.session_state.answer:
    left, right = st.columns([3, 2])
    with left:
        st.subheader("Recommendation")
        st.markdown(st.session_state.answer)
    with right:
        st.subheader(f"🧠 Memory used ({len(st.session_state.mems)})")
        if not st.session_state.mems:
            st.info("No memory used: generic answer.")
        for m in st.session_state.mems:
            st.code(m, language=None)

    st.divider()
    st.subheader("Close the loop: teach the agent")
    st.caption("This outcome is retained in Hindsight, so the next similar alert benefits.")
    c1, c2 = st.columns(2)
    service = c1.text_input("Service", value="payments-service")
    fix = c2.text_input("Fix you applied")
    root = st.text_input("Root cause (if known)")
    outcome = st.radio("Outcome", ["WORKED", "FAILED"], horizontal=True)
    if st.button("Save to memory") and fix:
        st.session_state.count += 1
        try:
            memory.retain_incident(dict(
                id=f"INC-{st.session_state.count}", service=service,
                date=dt.date.today().isoformat(), symptom=st.session_state["alert_box"],
                root_cause=root or "unknown", fix=fix, outcome=outcome))
            st.success("Retained. Run the same alert again and watch the answer change.")
        except Exception as e:
            st.error(f"Could not save to Hindsight: {e}")