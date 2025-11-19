
# Home IoT Monitoring

## Overview
This project is a modular IoT energy monitoring system using Python, PostgreSQL, RabbitMQ, and Metabase. It collects, processes, and visualizes energy consumption data from LG ThinQ devices.

### Architecture

![Architecture diagram](./home_iot.drawio.png)

### Components

- **ui**: FastAPI web interface for device management and energy sync. It displays registered/unregistered devices, allows registration and triggers energy sync by communicating with the coordinator.
- **coordinator**: FastAPI backend that manages device registration, sync requests, and orchestrates communication between the UI, RabbitMQ, and the database. It handles device registration, lists devices, and publishes sync requests to RabbitMQ.
- **etl_worker**: Python worker that listens to RabbitMQ for device sync requests, fetches energy data from LG API, and stores it in PostgreSQL.
- **postgres**: Database for storing device and energy consumption data.
- **rabbitmq**: Message broker for decoupling sync requests and ETL processing.
- **pgadmin**: Web-based PostgreSQL admin tool.
- **metabase**: Analytics and visualization platform for energy data, tt is used to visualize and do graphical analysis over energy consumption data.

## Setup

### Prerequisites

- LG API Access Token
- Docker & Docker Compose
- Python 3.12 (for local runs)
- Git

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=postgres
POSTGRES_HOME_IOT_DB=home_iot_db
POSTGRES_DEFAULT_DB=postgres

PGADMIN_ADMIN_EMAIL=your_pgadmin_email
PGADMIN_ADMIN_PASSWORD=your_pgadmin_password

LG_COUNTRY=BR
LG_API_KEY=your_lg_api_key
LG_CLIENT_ID=your_lg_client_id
LG_API_TOKEN=your_lg_api_token

RABBITMQ_HOST=rabbitmq
RABBITMQ_QUEUE=energy_consumption
```

Notice that it is necessary to generate an access token in order to make requests to the LG API. To do so you can follow the steps to create a Personal Access Token (PAT) defined in https://smartsolution.developer.lge.com/en/apiManage/thinq_connect?s=1763658624439#tag/PAT(Personal-Access-Token). 

This project assumes that there will be devices to fetch data from, otherwise you are gonna face an empty page when accessing the UI.

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/rqalbuquerque/home-iot.git
    cd home-iot
    ```

2. **Create and fill `.env` file** (see above).

3. **Build and start all services:**
    ```bash
    docker compose up --build
    ```

    This will start all containers and set up the network.

4. **Execute the required scripts (01, 02, and 03) in `sql/schema/` to create the database tables.**

### Running Modules Locally

#### UI

- Install dependencies:
   ```bash
   pip install -r ui/requirements.txt
   ```
- Run:
   ```bash
   uvicorn ui.main:app --reload --port 8080
   ```

#### Coordinator

- Install dependencies:
   ```bash
   pip install -r coordinator/requirements.txt
   ```
- Run:
   ```bash
   uvicorn coordinator.main:app --reload --port 8000
   ```

#### ETL Worker

- Install dependencies:
   ```bash
   pip install -r etl/requirements.txt
   ```
- Run:
   ```bash
   python etl/worker.py
   ```

#### Database

- SQL schema files are in `sql/schema/`. You can initialize the database manually if needed.

#### Metabase

- Access Metabase at [http://localhost:3000](http://localhost:3000) after starting Docker Compose.

#### PGAdmin

- Access PGAdmin at [http://localhost:5050](http://localhost:5050).

### Useful Docker Compose Commands

- Build without cache:
   ```bash
   docker compose build --no-cache
   ```
- Recreate containers:
   ```bash
   docker compose up -d --force-recreate
   ```
- Stop all services:
   ```bash
   docker compose down
   ```

## Persistence & Data

By default the project is configured to persist database and pgAdmin state using Docker named volumes. This prevents you from having to re-create the pgAdmin server connections or losing your Postgres data when containers are recreated.

- Postgres data is persisted in the named volume `postgres_data` and mounted at `/var/lib/postgresql` inside the container .
- pgAdmin state (saved server registrations, settings) is persisted in the named volume `pgadmin_data` at `/var/lib/pgadmin`.

Commands to bring up services (preserves volumes):
```bash
docker compose down   # stops containers but keeps named volumes
docker compose up -d --build
```

Notes:
- The pgAdmin login email/password are controlled by `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` in your `.env`. Once you register the Postgres server in the pgAdmin UI, that registration is stored in the `pgadmin_data` volume and will persist across restarts.
- If you prefer automatic pgAdmin server registration, I can add a `servers.json` provisioning file and mount it into the pgAdmin container so the server is pre-registered at container start.

If scaled, inspect `docker compose ps` to find the specific container names and use `docker logs -f <container_name>`.

## Folder Structure

- `ui/` - Web interface
- `coordinator/` - Backend API
- `etl/` - ETL worker and scripts
- `common/` - Shared modules
- `sql/` - Database schema
- `static/` - UI static files
