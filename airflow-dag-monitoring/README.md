# Airflow DAG Monitoring

Operational monitoring setup for Apache Airflow data pipelines.
Built to demonstrate DAG health monitoring, SLA tracking, and
incident response for a DataOps role.

## What's Inside

| File | Description |
|------|-------------|
| `pipeline_health_dag.py` | Hourly DAG that checks S3 file arrival and row count thresholds |
| `RUNBOOK.md` | Operational runbook for on-call DAG monitoring and incident response |

## DAG: `pipeline_health_monitor`

**Schedule:** Every hour  
**Purpose:** Detects pipeline failures before stakeholders notice

### Task Flow
```
check_s3_file_arrival → check_row_count_threshold → log_health_summary
```

- **check_s3_file_arrival** — Validates expected files landed in S3 within the hour
- **check_row_count_threshold** — Verifies ingested row counts fall within historical norms
- **log_health_summary** — Writes a structured health summary for post-incident review

## Key Concepts Demonstrated
- DAG authoring with proper `default_args` and retry logic
- XCom for passing data between tasks
- S3 integration via boto3
- Operational runbook structure for on-call support
- SLA breach detection pattern

## Stack
- Apache Airflow 2.x
- Python 3.10+
- AWS S3 (boto3)
- Snowflake (via SnowflakeHook in production)
