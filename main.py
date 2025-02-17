from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
origins = ["*"]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/")
def read_root():
  return {"Hello": "World"}

from routes import bins, clock, disk_info, meals, plants, todos, travel, weather

app.include_router(bins.router)
app.include_router(clock.router)
app.include_router(disk_info.router)
app.include_router(meals.router)
app.include_router(plants.router)
app.include_router(todos.router)
app.include_router(travel.router)
app.include_router(weather.router)
