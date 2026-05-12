# DataOps Portfolio

Hands-on projects covering the core tools of a DataOps / Platform Operations role.
Built to demonstrate operational thinking across pipeline monitoring,
infrastructure automation, and observability.

---

## Projects

### 1. Airflow DAG Monitoring
`/airflow-dag-monitoring`

Hourly health-check DAG that validates S3 file arrival and row count thresholds.
Includes an operational runbook for on-call incident response.

**Tools:** Apache Airflow 2.x · Python · AWS S3 · boto3

---

### 2. MSK / Kafka Operational Scripts
`/msk-kafka-ops`

Producer and consumer scripts for AWS MSK with consumer lag monitoring
and CloudWatch metric publishing for alerting and dashboards.

**Tools:** Python · kafka-python · AWS MSK · CloudWatch

---

### 3. Terraform AWS Infrastructure
`/terraform-aws-infra`

Infrastructure as Code for a DataOps landing zone: S3 bucket with lifecycle policies,
IAM roles for Snowflake storage integration, Lambda pipeline trigger, and SNS alerts.

**Tools:** Terraform · AWS S3 · IAM · Lambda · SNS

---

### 4. Prometheus + Grafana Monitoring Stack
`/prometheus-grafana-stack`

Docker Compose observability stack with Prometheus, Grafana, Alertmanager,
and Node Exporter. Includes PromQL alert rules for pipeline failures,
high CPU, and disk pressure.

**Tools:** Prometheus · Grafana · Alertmanager · Docker Compose

---

## Core Competencies Demonstrated

| Area | Skills |
|------|--------|
| Pipeline Ops | DAG authoring, SLA monitoring, incident runbooks |
| Streaming | Kafka producer/consumer, consumer lag, offset management |
| Cloud Infra | S3, IAM, Lambda, SNS via Terraform IaC |
| Observability | Prometheus scraping, PromQL alerts, Grafana dashboards |
| Python | boto3, kafka-python, operational automation scripts |

---

## About

I'm actively building hands-on experience in DataOps and Platform Operations,
focusing on the operational side of data infrastructure — keeping pipelines
healthy, deployments safe, and systems observable.

Currently learning: Snowflake RBAC · Jenkins CI/CD · ServiceNow change management
