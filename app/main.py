from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import bins, clock, disk_info, meals, plants, todos, travel, uklife, weather

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
origins = ["*"]

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
app.include_router(todos.router)
app.include_router(travel.router)
app.include_router(uklife.router)
app.include_router(weather.router)

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=5100)