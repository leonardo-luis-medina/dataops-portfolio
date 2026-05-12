"""
pipeline_health_dag.py
----------------------
DAG that monitors the health of upstream data pipelines.
Checks S3 file arrival, row count thresholds, and sends alerts
when anomalies are detected.

Author: DataOps Portfolio Project
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
import boto3
import logging

logger = logging.getLogger(__name__)

# ── Default arguments ────────────────────────────────────────────────────────
default_args = {
    "owner": "dataops",
    "depends_on_past": False,
    "email": ["dataops-alerts@company.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# ── DAG Definition ───────────────────────────────────────────────────────────
dag = DAG(
    dag_id="pipeline_health_monitor",
    default_args=default_args,
    description="Monitors S3 data arrival and pipeline health metrics",
    schedule_interval="0 * * * *",  # Every hour
    start_date=days_ago(1),
    catchup=False,
    tags=["monitoring", "dataops", "health-check"],
)

# ── Task Functions ───────────────────────────────────────────────────────────

def check_s3_file_arrival(**context):
    """
    Verify that expected files have landed in S3 within the SLA window.
    Raises an exception if files are missing, which triggers an alert.
    """
    s3 = boto3.client("s3")
    bucket = "company-data-landing"
    prefix = f"raw/events/{datetime.utcnow().strftime('%Y/%m/%d/%H')}/"
    expected_file_count = 1

    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    found = response.get("KeyCount", 0)

    logger.info(f"S3 check — prefix: {prefix} | found: {found} files")

    if found < expected_file_count:
        raise ValueError(
            f"SLA breach: expected {expected_file_count} file(s) at {prefix}, found {found}."
        )

    context["ti"].xcom_push(key="file_count", value=found)


def check_row_count_threshold(**context):
    """
    Pull row count from Snowflake staging table and validate it
    falls within the acceptable range based on historical averages.
    """
    # In production this would use SnowflakeHook
    # Simulated here for portfolio demonstration
    import random
    row_count = random.randint(8000, 12000)
    threshold_min = 5000
    threshold_max = 50000

    logger.info(f"Row count check: {row_count} rows ingested this hour")

    if not (threshold_min <= row_count <= threshold_max):
        raise ValueError(
            f"Row count anomaly: {row_count} is outside expected range "
            f"[{threshold_min}, {threshold_max}]"
        )

    context["ti"].xcom_push(key="row_count", value=row_count)


def log_health_summary(**context):
    """
    Aggregate results from upstream checks and write a summary
    to the monitoring log. Used for post-incident review.
    """
    ti = context["ti"]
    file_count = ti.xcom_pull(task_ids="check_s3_file_arrival", key="file_count")
    row_count = ti.xcom_pull(task_ids="check_row_count_threshold", key="row_count")

    summary = {
        "run_time": datetime.utcnow().isoformat(),
        "s3_files_found": file_count,
        "rows_ingested": row_count,
        "status": "HEALTHY",
    }

    logger.info(f"Pipeline health summary: {summary}")


# ── Task Definitions ─────────────────────────────────────────────────────────

t1_s3_check = PythonOperator(
    task_id="check_s3_file_arrival",
    python_callable=check_s3_file_arrival,
    provide_context=True,
    dag=dag,
)

t2_row_count = PythonOperator(
    task_id="check_row_count_threshold",
    python_callable=check_row_count_threshold,
    provide_context=True,
    dag=dag,
)

t3_summary = PythonOperator(
    task_id="log_health_summary",
    python_callable=log_health_summary,
    provide_context=True,
    dag=dag,
)

# ── Task Dependencies ────────────────────────────────────────────────────────
t1_s3_check >> t2_row_count >> t3_summary
