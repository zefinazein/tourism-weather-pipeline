FROM astrocrpublic.azurecr.io/runtime:3.3-8
RUN python3 -m venv /usr/local/airflow/dbt_venv && \
    /usr/local/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-core dbt-bigquery
