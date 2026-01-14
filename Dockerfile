FROM apache/airflow:2.7.3-python3.10

# Install additional system dependencies if needed
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
USER airflow

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy DAGs and other files
COPY dags/ /home/airflow/dags/
COPY config/ /home/airflow/config/

WORKDIR /home/airflow
