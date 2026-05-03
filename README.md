# Home API

A set of utilities relevant to a Home, used by the Home Portal project.

## Features

- Bin collection schedule
- Meal planning (with full history)
- Plant management
- Current weather, date, and time
- Disk space of the server
- Life in the UK Test (building tests and storing results)
- Travel information between 2 places

## Project Structure

**app/**

- `main.py` - Entrypoint for running the API
- `database.py` - Database connection manager and FastAPI dependency
- `util.py` - Utilities shared across the app
- `routers/` - Contains FastAPI routers for each utility service
- `services/` - Collection of services handling API logic
  - `main.py` - Main logic for a service
  - `models.py` - Models for a specific service. Used by the service and routes
- `resources/` - Static resources used by services
- `migrations/` - Database migration Python scripts

**/** (root)

- `scripts/` - Shell scripts for simple Docker deployment

## Development

See [pyproject.toml](pyproject.toml)

```
uv run fastapi dev --port=5100
```

### Lint

```
uv run ruff check .
```

### Type Check

```
uv run ty check .
```
