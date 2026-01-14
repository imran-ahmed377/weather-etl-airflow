# Weather ETL with Apache Airflow

A beginner-friendly Apache Airflow project that fetches weather data daily from a public API, transforms it, and saves it to a file.

## Project Overview

This project demonstrates core Airflow concepts:
- **DAGs (Directed Acyclic Graphs)**: Task dependency management
- **Operators**: Python operators for custom logic
- **Scheduling**: Daily task execution
- **Logging**: Task execution monitoring via Airflow UI
- **XCom**: Inter-task data passing

## Architecture

```
Fetch Weather API
        ↓
Transform Data
        ↓
Save to File
```

## Prerequisites

- Docker and Docker Compose (Recommended)
- OR: Python 3.10+, pip, virtualenv

## Quick Start with Docker

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/weather-etl-airflow.git
cd weather-etl-airflow
```

### 2. Build and start containers
```bash
docker-compose up -d
```

### 3. Access Airflow UI
- URL: http://localhost:8080
- Username: `admin`
- Password: `admin`

### 4. Enable the DAG
In the Airflow UI, find the `weather_etl` DAG and toggle it to "On"

### 5. View results
- Check the **Graph View** to see task dependencies
- Check **Logs** for task execution details
- Weather data is saved to `data/weather_*.json`

### 6. Stop containers
```bash
docker-compose down
```

## Local Development (Without Docker)

### 1. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Airflow
```bash
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

### 4. Start services
```bash
# Terminal 1
airflow webserver --port 8080

# Terminal 2
airflow scheduler
```

### 5. Access UI
Open http://localhost:8080 (admin/admin)

## Project Structure

```
weather-etl-airflow/
├── dags/
│   └── weather_etl_dag.py      # Main DAG definition
├── logs/                        # Airflow task logs
├── tests/                       # Unit tests
├── config/                      # Configuration files
├── data/                        # Output weather data
├── .github/
│   └── workflows/
│       └── airflow-ci.yml       # CI/CD pipeline
├── Dockerfile                   # Container configuration
├── docker-compose.yml           # Multi-container setup
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── .gitignore
```

## What the DAG Does

1. **Fetch Weather**: Calls Open-Meteo free weather API (no key needed)
2. **Transform**: Extracts temperature and humidity
3. **Save**: Stores data as JSON with timestamp

## Tasks

| Task | Purpose | Input | Output |
|------|---------|-------|--------|
| `fetch_weather` | Call weather API | - | Raw API response |
| `transform_weather` | Extract relevant fields | XCom from fetch | Cleaned data dict |
| `save_weather` | Write to disk | XCom from transform | JSON file |

## CI/CD Pipeline

GitHub Actions automatically:
- ✅ Validates DAG syntax
- ✅ Runs linting checks
- ✅ Executes tests on every push/PR

See `.github/workflows/airflow-ci.yml` for details.

## Extending the Project

### Add a new task
```python
def new_task():
    return "data"

task_new = PythonOperator(
    task_id='new_task',
    python_callable=new_task,
    dag=dag,
)

task_fetch >> task_new >> task_transform
```

### Change schedule
Edit the `schedule_interval` in the DAG:
- `@daily` → Daily at 00:00 UTC
- `@hourly` → Every hour
- `0 9 * * *` → Daily at 9 AM (cron format)

### Use different weather location
Edit the latitude/longitude in `fetch_weather()`:
```python
params = {
    "latitude": 40.7128,   # New York
    "longitude": -74.0060,
    ...
}
```

## Learning Resources

- [Apache Airflow Documentation](https://airflow.apache.org/)
- [Airflow Concepts](https://airflow.apache.org/docs/apache-airflow/stable/concepts/overview.html)
- [XCom Inter-task Communication](https://airflow.apache.org/docs/apache-airflow/stable/concepts/xcoms.html)

## Troubleshooting

### Docker issues
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d --build  # Rebuild
```

### Airflow webserver not accessible
```bash
docker-compose logs airflow  # Check logs
docker-compose restart airflow  # Restart container
```

### DAG not showing up
1. Check for syntax errors: `airflow dags validate`
2. Ensure DAG is in `dags/` folder
3. Restart scheduler

## License

MIT License

## Author

Created as a learning project for Apache Airflow fundamentals.
