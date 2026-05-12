from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'dataops',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='sales_pipeline',
    default_args=default_args,
    description='End-to-end sales data pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['dataops', 'sales'],
) as dag:

    generate_data = BashOperator(
        task_id='generate_data',
        bash_command='python /opt/airflow/scripts/generate_data.py',
    )

    run_etl = BashOperator(
        task_id='run_etl',
        bash_command='python /opt/airflow/scripts/etl.py',
    )

    generate_data >> run_etl
