# Home API

A set of utilities relevant to a Home, used by the Home Portal project.

## Features

- Bin collection schedule
- Meal planning and archiving
- Plant management
- Current weather, date, and time
- Disk space of the server
- To-do API
- Life in the UK Test (building tests and storing results)
- Travel information from a home to a target destination

## Project Structure

- `main.py` - Entrypoint for running the API
- `routers/` - Contains FastAPI routers for each utility service
- `services/` - Collection of services handling API logic
  - `main.py` - Main logic for a service
  - `models.py` - Models for a specific service. Used by the service and routes
- `resources/` - Static resources used by services
- `scripts/` - Shell scripts for simple Docker deployment
