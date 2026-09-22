from pathlib import Path
import sqlite3

if __package__:
    from .car_data import VOLVO_MODELS
else:
    from car_data import VOLVO_MODELS


DATABASE_PATH = Path(__file__).resolve().parent / "volvo.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS car_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS colors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS model_colors (
    model_id INTEGER NOT NULL,
    color_id INTEGER NOT NULL,
    PRIMARY KEY (model_id, color_id),
    FOREIGN KEY (model_id) REFERENCES car_models(id) ON DELETE CASCADE,
    FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS model_years (
    model_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    PRIMARY KEY (model_id, year),
    FOREIGN KEY (model_id) REFERENCES car_models(id) ON DELETE CASCADE
);
"""

def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.executescript(SCHEMA)

        for model_name, model_data in VOLVO_MODELS.items():
            connection.execute(
                "INSERT OR IGNORE INTO car_models (name) VALUES (?)",
                (model_name,),
            )
            model_id = connection.execute(
                "SELECT id FROM car_models WHERE name = ?",
                (model_name,),
            ).fetchone()["id"]

            for color_name in model_data["colors"]:
                connection.execute(
                    "INSERT OR IGNORE INTO colors (name) VALUES (?)",
                    (color_name,),
                )
                color_id = connection.execute(
                    "SELECT id FROM colors WHERE name = ?",
                    (color_name,),
                ).fetchone()["id"]
                connection.execute(
                    "INSERT OR IGNORE INTO model_colors (model_id, color_id) "
                    "VALUES (?, ?)",
                    (model_id, color_id),
                )

            connection.executemany(
                "INSERT OR IGNORE INTO model_years (model_id, year) VALUES (?, ?)",
                ((model_id, year) for year in model_data["years"]),
            )


def get_car_models(model_name=None):
    query = """
        SELECT
            car_models.id,
            car_models.name,
            GROUP_CONCAT(DISTINCT colors.name) AS colors
        FROM car_models
        LEFT JOIN model_colors ON model_colors.model_id = car_models.id
        LEFT JOIN colors ON colors.id = model_colors.color_id
        LEFT JOIN model_years ON model_years.model_id = car_models.id
    """
    parameters = []
    if model_name:
        query += " WHERE LOWER(car_models.name) = LOWER(?)"
        parameters.append(model_name)
    query += " GROUP BY car_models.id, car_models.name ORDER BY car_models.name"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()
        cars = []
        for row in rows:
            years = connection.execute(
                "SELECT year FROM model_years WHERE model_id = ? ORDER BY year",
                (row["id"],),
            ).fetchall()
            cars.append({
                "model": row["name"],
                "colors": sorted(row["colors"].split(",")) if row["colors"] else [],
                "years": [year["year"] for year in years],
            })
        return cars
