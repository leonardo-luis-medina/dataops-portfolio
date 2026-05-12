# Prometheus + Grafana Monitoring Stack

Docker Compose setup for a complete DataOps observability stack.
Monitors pipeline hosts, Airflow DAGs, and Snowflake environments
with alerting via Alertmanager.

## Stack Components

| Service | Port | Purpose |
|---------|------|---------|
| Prometheus | 9090 | Metrics collection and storage |
| Grafana | 3000 | Dashboards and visualization |
| Alertmanager | 9093 | Alert routing (email, Slack, PagerDuty) |
| Node Exporter | 9100 | Host-level metrics (CPU, memory, disk) |

## Quick Start

```bash
# Clone and start the stack
git clone <this-repo>
cd prometheus-grafana-stack
docker-compose up -d

# Verify all services are running
docker-compose ps
```

**Grafana:** http://localhost:3000 → admin / dataops123  
**Prometheus:** http://localhost:9090  
**Alertmanager:** http://localhost:9093

## What's Being Monitored

### Infrastructure
- CPU, memory, and disk usage on pipeline hosts (via Node Exporter)
- Service availability (`up` metric — fires if down > 2 min)

### Airflow
- DAG failure rate — alerts if > 3 failures per hour
- Scheduler heartbeat
- Task duration trends

### Snowflake (via custom exporter)
- Warehouse credit consumption
- Query queue depth
- Failed login attempts

## Alert Rules Summary

| Alert | Condition | Severity |
|-------|-----------|----------|
| InstanceDown | Host unreachable > 2m | Critical |
| HighCPUUsage | CPU > 85% for 5m | Warning |
| DiskSpaceLow | Disk < 15% free | Warning |
| AirflowDAGFailures | > 3 failures/hour | Critical |

## Key Files

```
prometheus-grafana-stack/
├── docker-compose.yml              # Full stack definition
├── prometheus/
│   ├── prometheus.yml              # Scrape configs and job targets
│   └── alert_rules.yml            # PromQL-based alert conditions
└── grafana/
    └── provisioning/
        └── datasources/
            └── prometheus.yml      # Auto-connects Grafana to Prometheus
```

## Stack
- Prometheus 2.51
- Grafana 10.4
- Alertmanager 0.27
- Node Exporter 1.7
- Docker + Docker Compose
