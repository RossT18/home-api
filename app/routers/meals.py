from app.database import DatabaseConnectionDep
import sqlite3
from app.services.meals.models import Meal, PartialMeal
from fastapi import APIRouter, HTTPException


router = APIRouter(prefix="/meals", tags=["meals"])


def init_meals_table(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            mealTime TEXT NOT NULL
        );
    """)


def row_to_meal(row: sqlite3.Row) -> Meal:
    return Meal(
        id=row["id"],
        name=row["name"],
        date=row["date"],
        mealTime=row["mealTime"],
    )


@router.post("/", response_model=Meal, status_code=201)
def create_meal(payload: Meal, db: DatabaseConnectionDep):
    cursor = db.execute(
        "INSERT INTO meals (name, date, mealTime) VALUES (?, ?, ?)",
        (payload.name, payload.date, payload.mealTime),
    )
    db.commit()
    row = db.execute("SELECT * FROM meals WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return row_to_meal(row)


@router.get("/", response_model=list[Meal])
def list_meals(db: DatabaseConnectionDep):
    return [row_to_meal(r) for r in db.execute("SELECT * FROM meals").fetchall()]


@router.get("/{meal_id}", response_model=Meal)
def get_meal(meal_id: int, db: DatabaseConnectionDep):
    row = db.execute("SELECT * FROM meals WHERE id = ?", (meal_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Meal not found")
    return row_to_meal(row)


@router.patch("/{meal_id}", response_model=Meal)
def update_meal(meal_id: int, payload: PartialMeal, db: DatabaseConnectionDep):
    raw = payload.model_dump()
    # Filter out None values.
    fields = {k: v for k, v in raw.items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    set_clause = ", ".join(f"{col} = ?" for col in fields)
    db.execute(
        f"UPDATE meals SET {set_clause} WHERE id = ?",
        [*fields.values(), meal_id],
    )
    db.commit()

    row = db.execute("SELECT * FROM meals WHERE id = ?", (meal_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Meal not found")
    return row_to_meal(row)


@router.delete("/{meal_id}", status_code=204)
def delete_meal(meal_id: int, db: DatabaseConnectionDep):
    result = db.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Meal not found")
