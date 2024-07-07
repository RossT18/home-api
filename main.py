from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
origins = [
  "http://localhost",
  "http://localhost:5173",
  "http://localhost:8000",
]

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

from routes import todos, clock, bins, meals, weather
app.include_router(todos.router)
app.include_router(clock.router)
app.include_router(bins.router)
app.include_router(meals.router)
app.include_router(weather.router)