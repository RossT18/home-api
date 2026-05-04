# Home API

A Python FastAPI for managing your meal plans, recording plants & scheduling watering days, and location-specific information for your home.

## Features

- Meal planning
- Plant management & watering
- Bin collection schedule
- Travel information between two places (usually your home and your favourite destination!)
- Current weather, date, and time at your home
- Disk space of the server
- Life in the UK Test (building tests and storing results)

## Diagram

![Diagram](.github/home-api-light.png#gh-light-mode-only)
![Diagram](.github/home-api-dark.png#gh-dark-mode-only)

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

## Motivation

Originally, I created this API to handle all information to display on my [badger2040w](https://github.com/pimoroni/badger2040). The project, then named HomeInk (Home + eInk), was to show home related glanceable information, including the next bin collection, current weather, and travel time to the city centre from home.

This developed into a new idea - a mobile app to show the same information, as well as new features like meal planning and house plant management. This is in a separate repository, `home-portal`, a React Router & TypeScript project.

The `home-portal` is now used by myself and my Wife daily (especially for my Wife to keep track of her 50+ plants and their various watering schedules).

A few people I know were applying for the Life in the UK test and found that mock test websites cannot keep track of score and are difficult to use. So I've included new endpoints to track scores from answering custom designed mock tests and run these tests in the `home-portal` app. Users can choose how many questions they would like from set categories, and if they want to include questions answered incorrectly before.

## Development

See [pyproject.toml](pyproject.toml)

### Run

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
