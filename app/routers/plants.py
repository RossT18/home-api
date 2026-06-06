from app.database import DatabaseConnectionDep
import sqlite3
from app.services.plants.models import Plant, PartialPlant, WaterEvent, DelayEvent
from fastapi import APIRouter, HTTPException

from datetime import timedelta
from app.util import convert_ISO_to_dt

router = APIRouter(prefix="/plants", tags=["plants"])


def init_plants_tables(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS water_plant_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (plant_id) REFERENCES plants(id)
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            iconName TEXT NOT NULL,
            purchaseDate TEXT NOT NULL,
            waterFrequency INTEGER NOT NULL,
            lightConditions TEXT NOT NULL,
            delayUntil TEXT
        );
    """)


def get_plant_water_history(plant_id: int, db: sqlite3.Connection) -> list[str]:
    rows = db.execute(
        "SELECT date FROM water_plant_events WHERE plant_id = ?", (plant_id,)
    ).fetchall()
    return [row["date"] for row in rows]


def row_to_plant(row: sqlite3.Row, db: sqlite3.Connection) -> Plant:
    return Plant(
        id=row["id"],
        name=row["name"],
        iconName=row["iconName"],
        purchaseDate=row["purchaseDate"],
        waterFrequency=row["waterFrequency"],
        lightConditions=row["lightConditions"],
        delayUntil=row["delayUntil"],
        waterHistory=get_plant_water_history(row["id"], db),
    )


@router.post("/", response_model=Plant, status_code=201)
def create_plant(payload: Plant, db: DatabaseConnectionDep):
    cursor = db.execute(
        "INSERT INTO plants (name, iconName, purchaseDate, waterFrequency, lightConditions, delayUntil) VALUES (?, ?, ?, ?, ?, ?)",
        (
            payload.name,
            payload.iconName,
            payload.purchaseDate,
            payload.waterFrequency,
            payload.lightConditions,
            payload.delayUntil,
        ),
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM plants WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return row_to_plant(row, db)


@router.get("/", response_model=list[Plant])
def list_plants(db: DatabaseConnectionDep):
    return [row_to_plant(r, db) for r in db.execute("SELECT * FROM plants").fetchall()]


@router.get("/{plant_id}", response_model=Plant)
def get_plant(plant_id: int, db: DatabaseConnectionDep):
    row = db.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return row_to_plant(row, db)


@router.patch("/{plant_id}", response_model=Plant)
def update_plant(plant_id: int, payload: PartialPlant, db: DatabaseConnectionDep):
    fields = payload.model_dump(exclude_unset=True)
    has_water_history = "waterHistory" in fields
    water_history = fields.pop("waterHistory", None)

    if not fields and not has_water_history:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    row = db.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Plant not found")

    if fields:
        set_clause = ", ".join(f"{col} = ?" for col in fields)
        db.execute(
            f"UPDATE plants SET {set_clause} WHERE id = ?",
            [*fields.values(), plant_id],
        )

    if has_water_history and water_history is not None:
        db.execute("DELETE FROM water_plant_events WHERE plant_id = ?", (plant_id,))
        db.executemany(
            "INSERT INTO water_plant_events (plant_id, date) VALUES (?, ?)",
            [(plant_id, water_date) for water_date in water_history],
        )

    db.commit()

    row = db.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    return row_to_plant(row, db)


@router.delete("/{plant_id}", status_code=204)
def delete_plant(plant_id: int, db: DatabaseConnectionDep):
    db.execute("DELETE FROM water_plant_events WHERE plant_id = ?", (plant_id,))
    result = db.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Plant not found")


@router.post("/water/{plant_ids}")
def water_plants(plant_ids: str, water_event: WaterEvent, db: DatabaseConnectionDep):
    date = water_event.date
    plant_ids_list = [plant_id.strip() for plant_id in plant_ids.split(",")]
    valid_plant_ids = []
    for plant_id in plant_ids_list:
        row = db.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
        if row is not None:
            valid_plant_ids.append(plant_id)

    for plant_id in valid_plant_ids:
        existing_water_event = db.execute(
            "SELECT * FROM water_plant_events WHERE plant_id = ? AND date = ?",
            (plant_id, date),
        ).fetchone()

        if existing_water_event is not None:
            db.execute(
                "DELETE FROM water_plant_events WHERE plant_id = ? AND date = ?",
                (plant_id, date),
            )
        else:
            db.execute(
                "INSERT INTO water_plant_events (plant_id, date) VALUES (?, ?)",
                (plant_id, date),
            )
            db.execute(
                """
                UPDATE plants
                SET delayUntil = NULL
                WHERE id = ? AND delayUntil IS NOT NULL AND delayUntil <= ?
                """,
                (plant_id, date),
            )
    db.commit()


@router.post("/delay/{plant_ids}")
def delay_plant_water(
    plant_ids: str, delay_event: DelayEvent, db: DatabaseConnectionDep
):
    plant_ids_list = [plant_id.strip() for plant_id in plant_ids.split(",")]

    plant_ids_placeholder = ",".join("?" * len(plant_ids_list))

    delay_until_date = convert_ISO_to_dt(delay_event.date) + timedelta(
        days=delay_event.days
    )
    delay_until_date_str = delay_until_date.strftime("%Y-%m-%d")

    db.execute(
        f"UPDATE plants SET delayUntil = ? WHERE id IN ({plant_ids_placeholder})",
        (delay_until_date_str, *plant_ids_list),
    )

    db.commit()
