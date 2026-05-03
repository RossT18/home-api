from argparse import ArgumentParser
import json
import sqlite3
import os
from app.routers import meals, plants
from app.database import get_db


def read_legacy_json_file(path: str) -> dict:
    with open(path, 'r') as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file at {path}: {e}")
            return {}

def migrate_meals(conn: sqlite3.Connection,data_folder: str) -> None:
    # Migrate `meal_plan.json` file to the meals table

    """
    Example of `meal_plan.json` file:
    {
        "1737276756129": {
            "name": "Meal Name",
            "date": "2025-01-21T08:52:36.000Z",
            "mealTime": "lunch"
        }...
    }
    """

    rows = conn.execute("SELECT COUNT(*) as count FROM meals").fetchone()
    if rows["count"] > 0:
        print(f"Meals table already has {rows['count']} rows. Skipping meals migration.")
        return


    file_path = os.path.join(data_folder, "meal_plan.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at {file_path}")
    legacy_meals = read_legacy_json_file(file_path)

    meals = [
        (meal["name"], meal["date"][:len("YYYY-MM-DD")], meal["mealTime"])
        for meal in legacy_meals.values()
    ]

    conn.executemany(
        "INSERT INTO meals (name, date, mealTime) VALUES (?, DATE(?), ?)",
        meals,
    )
    conn.commit()
    print(f"Migrated {len(meals)} meals.")

def migrate_plants(conn: sqlite3.Connection, data_folder: str) -> None:
    # Migrate `plants.json` file to the plants table

    """
    Example of `plants.json` file:
    {
        "1739033546259": {
            "name": "Plant 1",
            "iconName": "pagelines",
            "purchaseDate": "2025-02-07",
            "waterFrequency": 2,
            "lightConditions": "Some",
            "waterHistory": [
            "2025-01-31",
            "2025-02-14"
            ],
            "delayUntil": "2025-03-05"
        }...
    }
    """
    rows = conn.execute("SELECT COUNT(*) as count FROM plants").fetchone()
    if rows["count"] > 0:
        print(f"Plants table already has {rows['count']} rows. Skipping plants migration.")
        return

    file_path = os.path.join(data_folder, "plants.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at {file_path}")
    legacy_plants = read_legacy_json_file(file_path)

    for plant in legacy_plants.values():
        plant_id = conn.execute(
            "INSERT INTO plants (name, iconName, purchaseDate, waterFrequency, lightConditions, delayUntil) VALUES (?, ?, ?, ?, ?, ?)",
            (plant["name"], plant["iconName"], plant["purchaseDate"], plant["waterFrequency"], plant["lightConditions"], plant["delayUntil"])
        ).lastrowid

        water_history = plant.get("waterHistory", [])
        for water_date in water_history:
            conn.execute(
                "INSERT INTO water_plant_events (plant_id, date) VALUES (?, DATE(?))",
                (plant_id, water_date)
            )
    conn.commit()

    print(f"Migrated {len(legacy_plants)} plants.")

def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--data-folder', type=str, help='Path to the legacy data folder', required=True)
    args = parser.parse_args()
    data_folder_path = os.path.abspath(args.data_folder)
    if not data_folder_path:
        raise ValueError("Data folder path cannot be empty")
    if not os.path.isdir(data_folder_path):
        raise NotADirectoryError(f"Provided data folder path is not a directory: {data_folder_path}")
    print(f"Using data folder: {data_folder_path}")

    print("Connecting to database...")
    db_gen = get_db()
    conn = next(db_gen)

    print("Initializing database tables...")
    meals.init_meals_table(conn)
    plants.init_plants_tables(conn)

    print("Migrating meals...")
    migrate_meals(conn, data_folder_path)

    print("Migrating plants...")
    migrate_plants(conn, data_folder_path)

    print("Data migration completed successfully.")

if __name__ == "__main__":
    main()
