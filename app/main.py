from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from app.database import database_path
from app.routers import bins, clock, disk_info, meals, plants, travel, uklife, weather


load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    with sqlite3.connect(database_path) as conn:
        meals.init_meals_table(conn)
        plants.init_plants_tables(conn)
        conn.commit()
    yield
    # Shutdown logic (e.g. closing a connection pool) would go here

app = FastAPI(
  title='Home API',
  lifespan=lifespan
)

origins = ['*']

app.add_middleware(
  CORSMiddleware,  # ty:ignore[invalid-argument-type]
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/")
def read_root():
  return health()

@app.get('/health')
def health():
  return {"status": "healthy"}


app.include_router(bins.router)
app.include_router(clock.router)
app.include_router(disk_info.router)
app.include_router(meals.router)
app.include_router(plants.router)
app.include_router(travel.router)
app.include_router(uklife.router)
app.include_router(weather.router)

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=5100)