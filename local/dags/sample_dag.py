from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.S3_hook import S3Hook
from datetime import datetime

default_args = {
    "owner": "airflow",
    "start_date": datetime(2021, 10, 1),
}

def read_file():
    hook = S3Hook()
    file_content = hook.read_key(
        key="customer.csv", bucket_name="my-landing-bucket"
    )    
    print(file_content)
    
with DAG("sample_dag", schedule_interval=None, catchup=False, default_args=default_args) as dag:t1 = PythonOperator(
        task_id='read_s3_file',
        python_callable=read_file
)