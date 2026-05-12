"""
kafka_ops.py
------------
Producer and Consumer scripts for MSK (Managed Streaming for Kafka) on AWS.
Demonstrates operational patterns for monitoring consumer lag,
handling offset management, and detecting anomalies.

Author: DataOps Portfolio Project
"""

import json
import time
import logging
import boto3
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
MSK_BOOTSTRAP_SERVERS = [
    "b-1.msk-cluster.abc123.kafka.us-east-1.amazonaws.com:9092",
    "b-2.msk-cluster.abc123.kafka.us-east-1.amazonaws.com:9092",
]
TOPIC_NAME = "customer-events"
CONSUMER_GROUP = "dataops-consumer-group"


# ── Producer ──────────────────────────────────────────────────────────────────

class EventProducer:
    """
    Publishes customer events to MSK topic.
    Includes error handling and delivery confirmation logging.
    """

    def __init__(self, bootstrap_servers=MSK_BOOTSTRAP_SERVERS):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",           # Wait for all replicas to acknowledge
            retries=3,
            retry_backoff_ms=500,
        )

    def publish_event(self, event: dict):
        """Send a single event, log success or failure."""
        try:
            future = self.producer.send(TOPIC_NAME, value=event)
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Event published | topic={record_metadata.topic} "
                f"partition={record_metadata.partition} "
                f"offset={record_metadata.offset}"
            )
        except KafkaError as e:
            logger.error(f"Failed to publish event: {e}")
            raise

    def flush_and_close(self):
        self.producer.flush()
        self.producer.close()


# ── Consumer ──────────────────────────────────────────────────────────────────

class EventConsumer:
    """
    Consumes events from MSK topic.
    Tracks consumer lag and raises alerts when lag exceeds threshold.
    """

    LAG_ALERT_THRESHOLD = 1000  # messages

    def __init__(self, bootstrap_servers=MSK_BOOTSTRAP_SERVERS):
        self.consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=bootstrap_servers,
            group_id=CONSUMER_GROUP,
            auto_offset_reset="earliest",
            enable_auto_commit=False,      # Manual commit for reliability
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            max_poll_records=500,
        )

    def check_consumer_lag(self):
        """
        Calculate consumer lag per partition.
        Logs a warning if lag exceeds threshold — key operational signal.
        """
        lag_per_partition = {}
        partitions = self.consumer.assignment()

        end_offsets = self.consumer.end_offsets(partitions)
        for partition in partitions:
            committed = self.consumer.committed(partition) or 0
            end = end_offsets[partition]
            lag = end - committed
            lag_per_partition[partition.partition] = lag

            if lag > self.LAG_ALERT_THRESHOLD:
                logger.warning(
                    f"HIGH LAG DETECTED | partition={partition.partition} "
                    f"lag={lag} | threshold={self.LAG_ALERT_THRESHOLD}"
                )

        logger.info(f"Consumer lag report: {lag_per_partition}")
        return lag_per_partition

    def consume_events(self, max_messages=100):
        """
        Poll and process messages with manual offset commits.
        """
        processed = 0
        for message in self.consumer:
            event = message.value
            logger.info(
                f"Consumed | partition={message.partition} "
                f"offset={message.offset} | event_id={event.get('id')}"
            )
            # Process event here (e.g., write to Snowflake staging)
            self._process_event(event)

            # Commit after successful processing
            self.consumer.commit()
            processed += 1

            if processed >= max_messages:
                break

        logger.info(f"Consumed {processed} messages")

    def _process_event(self, event: dict):
        """Placeholder for downstream processing logic."""
        logger.debug(f"Processing event: {event}")

    def close(self):
        self.consumer.close()


# ── CloudWatch Lag Publisher ──────────────────────────────────────────────────

def publish_lag_to_cloudwatch(lag_per_partition: dict, cluster_name: str):
    """
    Push consumer lag metrics to CloudWatch for Grafana dashboards
    and alerting via CloudWatch Alarms.
    """
    cw = boto3.client("cloudwatch", region_name="us-east-1")
    metric_data = []

    for partition, lag in lag_per_partition.items():
        metric_data.append({
            "MetricName": "ConsumerLag",
            "Dimensions": [
                {"Name": "ClusterName", "Value": cluster_name},
                {"Name": "ConsumerGroup", "Value": CONSUMER_GROUP},
                {"Name": "Partition", "Value": str(partition)},
            ],
            "Value": lag,
            "Unit": "Count",
            "Timestamp": datetime.utcnow(),
        })

    cw.put_metric_data(Namespace="DataOps/Kafka", MetricData=metric_data)
    logger.info(f"Published {len(metric_data)} lag metrics to CloudWatch")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Demo: produce 5 test events
    producer = EventProducer()
    for i in range(5):
        producer.publish_event({
            "id": f"evt-{i}",
            "type": "page_view",
            "user_id": f"user-{i * 10}",
            "timestamp": datetime.utcnow().isoformat(),
        })
    producer.flush_and_close()

    # Demo: consume and check lag
    consumer = EventConsumer()
    consumer.consume_events(max_messages=5)
    lag = consumer.check_consumer_lag()
    publish_lag_to_cloudwatch(lag, cluster_name="prod-msk-cluster")
    consumer.close()
