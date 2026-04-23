from app.routers import meals, plants, uklife
from app.database import get_db




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



# Migrate `plants.json` file to the plants table

# Migrate `uklife_scores.json` file to the uklife_results table


def main():
    print("Migrating legacy JSON data...")
    db_gen = get_db()
    conn = next(db_gen)
    
    meals.init_meals_table(conn)
    plants.init_plants_tables(conn)
    uklife.init_uklife_tables(conn)

if __name__ == "__main__":
    main()
