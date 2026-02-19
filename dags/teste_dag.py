from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def print_teste():
    print("Teste")
    return "O Docker está funcionando"

with DAG(
    'dag_de_teste_conexao',
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False
) as dag:

    # 3. Definição da Task
    task_teste = PythonOperator(
        task_id='printar_mensagem_no_log',
        python_callable=print_teste
    )