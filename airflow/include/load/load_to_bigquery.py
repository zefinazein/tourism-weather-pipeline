from dotenv import load_dotenv
load_dotenv()

from google.cloud import bigquery
import pandas as pd
import os

client = bigquery.Client(project="tourism-weather-de")
dataset = "raw"

def load_csv(csv_path, table_name, write_disposition="WRITE_TRUNCATE", date_cols=None):
    df = pd.read_csv(csv_path, parse_dates=date_cols or [])
    table_id = f"{client.project}.{dataset}.{table_name}"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        autodetect=True
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {len(df)} rows into {table_id}")

load_csv("data/raw/bps/output_bps.csv", "raw_bps_kunjungan")
load_csv("data/raw/openmeteo/raw_cuaca.csv", "raw_openmeteo_cuaca")
load_csv("data/raw/google_trends/raw_google_trends.csv", "raw_google_trends")