"""Loads synthetic past incidents into Hindsight. Run once: python seed.py
Run test_connection.py first if this fails."""
from memory import retain_incident

INCIDENTS = [
 dict(id="INC-101", service="payments-service", date="2026-01-09",
  symptom="5xx spike, 'connection pool exhausted' errors right after Friday deploy",
  root_cause="Deploy raised worker count to 40 but DB pool max stayed at 20",
  fix="Restarted payments-service pods", outcome="FAILED - errors returned within 4 minutes"),
 dict(id="INC-102", service="payments-service", date="2026-01-09",
  symptom="Same pool exhaustion errors after restart, checkout latency 12s",
  root_cause="Deploy raised worker count to 40 but DB pool max stayed at 20",
  fix="Rolled back to previous release v2.14.1", outcome="WORKED - recovered in 3 minutes"),
 dict(id="INC-103", service="payments-service", date="2026-02-20",
  symptom="Timeouts to Postgres, pool exhausted, started after config change on Friday",
  root_cause="Config change lowered DB_POOL_MAX from 40 to 10",
  fix="Restarted pods", outcome="FAILED - config was reloaded with the same bad value"),
 dict(id="INC-104", service="payments-service", date="2026-02-20",
  symptom="Pool exhaustion continuing after restart",
  root_cause="Config change lowered DB_POOL_MAX from 40 to 10",
  fix="Reverted config in Git and redeployed", outcome="WORKED - recovered in 5 minutes"),
 dict(id="INC-105", service="search-api", date="2026-02-27",
  symptom="p99 latency 8s, Elasticsearch heap at 95%",
  root_cause="Unbounded wildcard queries from a new partner integration",
  fix="Rate-limited partner API key and restarted ES data node", outcome="WORKED"),
 dict(id="INC-106", service="auth-service", date="2026-03-03",
  symptom="Login failures, 'JWT signature invalid' for ~15% of users",
  root_cause="One pod had a stale signing key after secret rotation",
  fix="Restarted only the stale pod after verifying key hash", outcome="WORKED - restart IS the right fix here"),
 dict(id="INC-107", service="notifications-worker", date="2026-03-14",
  symptom="Queue depth growing to 2M, emails delayed 40 minutes",
  root_cause="SMTP provider throttling after IP reputation drop",
  fix="Scaled workers from 5 to 20", outcome="FAILED - made throttling worse"),
 dict(id="INC-108", service="notifications-worker", date="2026-03-14",
  symptom="Queue still growing after scale-up",
  root_cause="SMTP provider throttling after IP reputation drop",
  fix="Failed over to secondary SMTP provider", outcome="WORKED - queue drained in 25 minutes"),
 dict(id="INC-109", service="checkout-web", date="2026-04-02",
  symptom="Blank page for Safari users, JS error on load",
  root_cause="Build used a regex lookbehind unsupported in older Safari",
  fix="Rolled back frontend bundle", outcome="WORKED"),
 dict(id="INC-110", service="ledger-db", date="2026-04-18",
  symptom="Replication lag 90s, read replicas serving stale balances",
  root_cause="Long-running analytics query holding locks on primary",
  fix="Killed the analytics query and moved it to a dedicated replica", outcome="WORKED"),
]

if __name__ == "__main__":
    for inc in INCIDENTS:
        retain_incident(inc)
        print("retained", inc["id"])
    print(f"Done: {len(INCIDENTS)} incidents stored in Hindsight.")
