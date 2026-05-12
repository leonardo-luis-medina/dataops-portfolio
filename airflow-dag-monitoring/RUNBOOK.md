# Airflow DAG Monitoring — Operational Runbook

## Overview
This runbook covers day-to-day monitoring and incident response for
Airflow DAGs in the DataOps platform. Reference this during on-call shifts
and maintenance windows.

---

## 1. Daily Health Checks

| Check | Where | Expected |
|-------|-------|----------|
| All DAGs green | Airflow UI → Browse → DAG Runs | No `failed` state |
| Scheduler heartbeat | Admin → Metrics | Last heartbeat < 30s ago |
| Task queue depth | Admin → Celery Flower | Workers not saturated |
| S3 file arrival | CloudWatch → `s3-landing-monitor` | 0 missing file alerts |

---

## 2. Common Failure Scenarios

### DAG stuck in `running` state
**Symptoms:** Task has been running longer than its SLA.
**Steps:**
1. Open Airflow UI → click the DAG → Graph View
2. Identify the stuck task (yellow border = running)
3. Check task logs: click task → Log
4. If log shows no progress for 15+ min → clear the task:
   - CLI: `airflow tasks clear <dag_id> -t <task_id> -s <start_date>`
5. If issue persists, escalate to data engineering with the log output

### DAG in `failed` state
**Steps:**
1. Click failed DAG run → identify red task
2. Read the error in logs — note the full traceback
3. Check if it's transient (network timeout, S3 throttle) → retry once
4. If it's a data issue (bad schema, null values) → do NOT retry, open a Jira ticket
5. Notify stakeholders within 15 minutes if SLA is breached

### Scheduler not running
**Steps:**
1. SSH into Airflow scheduler host
2. Check process: `ps aux | grep airflow`
3. Restart scheduler: `systemctl restart airflow-scheduler`
4. Verify: `airflow jobs check --job-type SchedulerJob --hostname <host>`

---

## 3. Escalation Path

```
On-call DataOps Engineer
        ↓ (15 min no resolution)
Senior Data Engineer
        ↓ (30 min no resolution)
Engineering Manager + Stakeholder comms
```

---

## 4. Post-Incident Checklist
- [ ] Root cause identified
- [ ] Timeline documented
- [ ] Stakeholders notified of resolution
- [ ] Jira ticket created with RCA
- [ ] Runbook updated if new scenario discovered
