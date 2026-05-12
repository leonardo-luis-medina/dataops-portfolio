# Terraform AWS Infrastructure — DataOps

Infrastructure as Code for the DataOps platform on AWS.
Manages S3 data landing zones, IAM roles for Snowflake integration,
Lambda pipeline triggers, and SNS alerting.

## Resources Provisioned

| Resource | Purpose |
|----------|---------|
| `aws_s3_bucket` | Data landing zone for raw pipeline files |
| `aws_iam_role` (Snowflake) | Allows Snowflake to read from S3 via storage integration |
| `aws_iam_role` (Lambda) | Execution role for pipeline trigger function |
| `aws_lambda_function` | Triggered on S3 file upload, kicks off pipeline |
| `aws_sns_topic` | Pipeline failure alerts to on-call team |

## Architecture
```
S3 Upload (raw/)
    └── S3 Event Notification
            └── Lambda (pipeline-trigger)
                    ├── Triggers Airflow DAG via API
                    └── SNS alert on failure
                            └── PagerDuty / Email
```

## Usage

```bash
# Initialize with remote state
terraform init

# Plan for dev environment
terraform plan -var="env=dev"

# Apply
terraform apply -var="env=dev"

# Destroy (be careful in prod)
terraform destroy -var="env=dev"
```

## Key Design Decisions

**Remote state in S3** — Team members share the same state file,
preventing infrastructure drift when multiple engineers apply changes.

**Snowflake IAM trust with ExternalId** — The `sts:ExternalId` condition
prevents the confused deputy problem when Snowflake assumes your role.

**S3 public access block** — All four block settings are enabled.
Data buckets should never be public, regardless of bucket policy.

**90-day lifecycle on raw/** — Raw files expire automatically,
keeping storage costs predictable without manual cleanup.

## Stack
- Terraform >= 1.5.0
- AWS Provider ~> 5.0
- Remote state: S3 + DynamoDB lock
