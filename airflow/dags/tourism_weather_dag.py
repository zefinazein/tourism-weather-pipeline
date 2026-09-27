from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.constants import ExecutionMode
from cosmos.profiles import GoogleCloudServiceAccountFileProfileMapping

DBT_PROJECT_PATH = "/usr/local/airflow/include/dbt_project"

profile_config = ProfileConfig(
    profile_name="dbt_project",
    target_name="dev",
    profile_mapping=GoogleCloudServiceAccountFileProfileMapping(
        conn_id="google_cloud_default",
        profile_args={"project": "tourism-weather-de", "dataset": "warehouse"},
    ),
)

execution_config = ExecutionConfig(
    dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt",
)

default_args = {"retries": 2}

with DAG(
    "tourism_weather_pipeline",
    schedule="@monthly",
    start_date=datetime(2026, 1, 1),
    default_args=default_args,
    catchup=False,
) as dag:

    GCP_KEY_PATH = "/usr/local/airflow/include/keys/tourism-weather-de-240ef6b2521b.json"

    extract_openmeteo = BashOperator(
        task_id="extract_openmeteo",
        bash_command="cd /usr/local/airflow/include/extract && python fetch_openmeteo.py",
    )

    extract_trends = BashOperator(
        task_id="extract_trends",
        bash_command="cd /usr/local/airflow/include/extract && python fetch_google_trends.py",
    )

    import_bps = BashOperator(
        task_id="import_bps",
        bash_command="cd /usr/local/airflow/include/extract && python import_bps.py",
    )

    load_to_bq = BashOperator(
        task_id="load_to_bigquery",
        bash_command="cd /usr/local/airflow/include && python load/load_to_bigquery.py",
        env={"GOOGLE_APPLICATION_CREDENTIALS": GCP_KEY_PATH},
        append_env=True,
    )

    dbt_transform = DbtTaskGroup(
        group_id="dbt_transform",
        project_config=ProjectConfig(DBT_PROJECT_PATH),
        profile_config=profile_config,
        execution_config=execution_config,
    )

    [extract_openmeteo, extract_trends, import_bps] >> load_to_bq >> dbt_transform