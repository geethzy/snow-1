from datetime import datetime
from airflow import dag
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import boto3
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 30),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

def extract(**kwargs):
    logging.info('Starting extract function')
    path = '/home/geeth/workarea/airflow_projects/airtravels.csv'
    df = pd.read_csv(path)
    kwargs['ti'].xcom_push(key='extracted_data', value=df)
    logging.info('Extract function completed')
    logging.info(df.head(5))
 
def transform(**kwargs):
    logging.info('Starting transform function')
    data = kwargs['ti'].xcom_pull(key='extracted_data')
    logging.info(data.head(5))
    data.columns = data.columns.str.replace('"', '')
    data.columns = data.columns.str.strip()
    data['Total'] = data['1958'] + data['1959'] + data['1960']
    kwargs['ti'].xcom_push(key='transformed_data', value=data)
    logging.info('Transform function completed')
 
def load(**kwargs):
    logging.info('Starting load function')
    data = kwargs['ti'].xcom_pull(key='transformed_data')
    s3 = boto3.resource('s3')
    bucket = 'my-airflow-dags-bucket'
    csv_buffer = StringIO()
    data.to_csv(csv_buffer)
    filename = f"airtravel/transformed/{datetime.now().strftime('%Y-%m-%d')}.csv"
    s3.Object(bucket, filename).put(Body=csv_buffer.getvalue())
    logging.info('Load function completed, data loaded to s3')

task_extract = PythonOperator(
    task_id='extract',
    python_callable=extract,
    provide_context=True,
    dag=dag
)
 
task_transform = PythonOperator(
    task_id='transform',
    python_callable=transform,
    provide_context=True,
    dag=dag
)
 
task_load = PythonOperator(
    task_id='load',
    python_callable=load,
    provide_context=True,
    dag=dag
)


task_extract >> task_transform >> task_load