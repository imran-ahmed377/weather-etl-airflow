"""
Weather ETL DAG

This DAG fetches weather data from a free public API, transforms it,
and saves it to a local file daily.

Dependencies:
- requests: HTTP library
- pandas: Data manipulation (optional)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Default arguments for all tasks
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2026, 1, 13),
}

# DAG definition
dag = DAG(
    'weather_etl',
    default_args=default_args,
    description='Daily weather ETL pipeline with fetch, transform, and save tasks',
    schedule_interval='@daily',  # Runs daily at 00:00 UTC
    catchup=False,  # Don't backfill historical runs
    tags=['etl', 'weather', 'beginner'],
)


def fetch_weather():
    """
    Task 1: Fetch weather data from Open-Meteo free API

    Open-Meteo is a free weather API that requires no API key.
    Location: London, UK

    Returns:
        dict: JSON response from weather API
    """
    logger.info("Starting weather fetch task...")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 51.5074,        # London latitude
        "longitude": -0.1278,       # London longitude
        "current": "temperature_2m,relative_humidity_2m,weather_code",
        "timezone": "UTC"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Successfully fetched weather data: {data}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        raise


def transform_weather(**context):
    """
    Task 2: Transform raw weather data

    Extracts relevant fields from the API response using XCom.

    Args:
        context: Airflow context, used to pull data from XCom

    Returns:
        dict: Transformed weather data with timestamp
    """
    logger.info("Starting weather transform task...")

    # Get data from previous task using XCom
    raw_data = context['task_instance'].xcom_pull(task_ids='fetch_weather')

    if not raw_data:
        raise ValueError("No weather data received from fetch task")

    # Extract current weather
    current = raw_data.get('current', {})

    # Transform: keep only relevant fields
    transformed = {
        'timestamp': datetime.now().isoformat(),
        'location': {
            'name': 'London',
            'latitude': 51.5074,
            'longitude': -0.1278,
        },
        'weather': {
            'temperature_celsius': current.get('temperature_2m'),
            'humidity_percent': current.get('relative_humidity_2m'),
            'weather_code': current.get('weather_code'),
        }
    }

    logger.info(f"Transformed weather data: {transformed}")
    return transformed


def save_weather(**context):
    """
    Task 3: Save transformed weather data to file

    Saves the transformed data as JSON with a timestamp-based filename.
    Creates 'data' directory if it doesn't exist.

    Args:
        context: Airflow context, used to pull data from XCom
    """
    logger.info("Starting weather save task...")

    # Get transformed data from previous task using XCom
    weather_data = context['task_instance'].xcom_pull(
        task_ids='transform_weather')

    if not weather_data:
        raise ValueError("No weather data received from transform task")

    # Create data directory if it doesn't exist
    output_dir = Path('/home/airflow/data')  # Docker path
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = output_dir / f"weather_{timestamp}.json"

    # Write to file
    try:
        with open(file_path, 'w') as f:
            json.dump(weather_data, f, indent=2)
        logger.info(f"Weather data successfully saved to {file_path}")
        return str(file_path)
    except IOError as e:
        logger.error(f"Error saving weather data: {str(e)}")
        raise


# Create task instances
task_fetch = PythonOperator(
    task_id='fetch_weather',
    python_callable=fetch_weather,
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_weather',
    python_callable=transform_weather,
    dag=dag,
)

task_save = PythonOperator(
    task_id='save_weather',
    python_callable=save_weather,
    dag=dag,
)

# Define task dependencies: fetch -> transform -> save
task_fetch >> task_transform >> task_save
