# hatch-messaging
A messaging service for Hatch

## Development

### Requirements
- Docker & Docker Compose
- Python 3.11 (for local development)

### Quick Start

1. Build and start the services:
   ```bash
   docker compose up --build
   ```
2. The Django app will be available at http://localhost:8000
3. The Postgres database will be available at localhost:5432

### Local Development (without Docker)

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Set environment variables for Postgres connection or update `settings.py`.
3. Run migrations and start the server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Project Structure
- `hatch_messaging/` - Django project and app code
- `docker-compose.yml` - Multi-service orchestration
- `Dockerfile` - Django app container
- `requirements.txt` - Python dependencies

---
