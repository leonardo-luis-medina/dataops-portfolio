# MSK / Kafka Operational Scripts

Python scripts for operating and monitoring AWS MSK (Managed Streaming for Kafka)
clusters in a DataOps environment.

## What's Inside

| File | Description |
|------|-------------|
| `kafka_ops.py` | Producer, consumer, lag monitoring, and CloudWatch metric publishing |

## Key Operational Patterns

### Consumer Lag Monitoring
Consumer lag = messages produced - messages consumed. High lag means
your consumers are falling behind, which causes data freshness issues downstream.

This script:
- Calculates lag per partition
- Logs a warning when lag exceeds 1,000 messages
- Publishes lag as a CloudWatch custom metric for dashboards and alarms

### Manual Offset Commits
Auto-commit can cause message loss on consumer crash. This script
uses `enable_auto_commit=False` and commits only after successful processing —
the standard pattern for reliable DataOps pipelines.

### CloudWatch Integration
Lag metrics are pushed to the `DataOps/Kafka` namespace in CloudWatch,
where they can be visualized in Grafana or trigger SNS alerts.

## Architecture
```
MSK Cluster (multi-AZ)
    ├── Topic: customer-events (3 partitions, replication factor 2)
    ├── Producer → publishes events with acks=all
    └── Consumer Group: dataops-consumer-group
            └── Lag metrics → CloudWatch → Grafana Dashboard
```

## Stack
- AWS MSK (Kafka 3.x)
- Python kafka-python library
- boto3 for CloudWatch integration
- Prometheus + Grafana for visualization (see `prometheus-grafana-stack`)
