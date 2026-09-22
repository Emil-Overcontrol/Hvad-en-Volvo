import sqlite3
from pathlib import Path

from car_data import VOLVO_MODELS

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "volvo.sqlite3"


def _connect(db_path=None):
    target = Path(db_path) if db_path else DEFAULT_DB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(target), target


def initialize_database(db_path=None):
    conn, target = _connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS car_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS colors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS model_colors (
                model_id INTEGER NOT NULL,
                color_id INTEGER NOT NULL,
                PRIMARY KEY (model_id, color_id),
                FOREIGN KEY (model_id) REFERENCES car_models(id),
                FOREIGN KEY (color_id) REFERENCES colors(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS model_years (
                model_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                PRIMARY KEY (model_id, year),
                FOREIGN KEY (model_id) REFERENCES car_models(id)
            )
            """
        )

        for model_name, details in VOLVO_MODELS.items():
            conn.execute(
                "INSERT OR IGNORE INTO car_models (name) VALUES (?)",
                (model_name,),
            )
            model_row = conn.execute(
                "SELECT id FROM car_models WHERE name = ?",
                (model_name,),
            ).fetchone()
            if model_row is None:
                continue
            model_id = model_row[0]

            for color in details["colors"]:
                conn.execute(
                    "INSERT OR IGNORE INTO colors (name) VALUES (?)",
                    (color,),
                )
                color_row = conn.execute(
                    "SELECT id FROM colors WHERE name = ?",
                    (color,),
                ).fetchone()
                if color_row is None:
                    continue
                conn.execute(
                    "INSERT OR IGNORE INTO model_colors (model_id, color_id) VALUES (?, ?)",
                    (model_id, color_row[0]),
                )

            for year in details["years"]:
                conn.execute(
                    "INSERT OR IGNORE INTO model_years (model_id, year) VALUES (?, ?)",
                    (model_id, int(year)),
                )

        conn.commit()
    finally:
        conn.close()

    return str(target)


def ensure_database_exists(db_path=None):
    target = Path(db_path) if db_path else DEFAULT_DB_PATH
    if not target.exists():
        initialize_database(target)
        return

    with sqlite3.connect(target) as conn:
        table_exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='car_models'"
        ).fetchone()
        if table_exists is None:
            initialize_database(target)


def get_car_models(model_name=None, db_path=None):
    target = Path(db_path) if db_path else DEFAULT_DB_PATH
    ensure_database_exists(target)

    with sqlite3.connect(target) as conn:
        if model_name is None:
            rows = conn.execute(
                """
                SELECT cm.name, GROUP_CONCAT(my.year, ',') AS years, GROUP_CONCAT(c.name, ',') AS colors
                FROM car_models cm
                LEFT JOIN model_years my ON my.model_id = cm.id
                LEFT JOIN model_colors mc ON mc.model_id = cm.id
                LEFT JOIN colors c ON c.id = mc.color_id
                GROUP BY cm.id, cm.name
                ORDER BY cm.name
                """
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT cm.name, GROUP_CONCAT(my.year, ',') AS years, GROUP_CONCAT(c.name, ',') AS colors
                FROM car_models cm
                LEFT JOIN model_years my ON my.model_id = cm.id
                LEFT JOIN model_colors mc ON mc.model_id = cm.id
                LEFT JOIN colors c ON c.id = mc.color_id
                WHERE LOWER(cm.name) = LOWER(?)
                GROUP BY cm.id, cm.name
                ORDER BY cm.name
                """,
                (model_name,),
            ).fetchall()

        cars = []
        for name, years_csv, colors_csv in rows:
            years = []
            if years_csv:
                years = sorted({int(year) for year in years_csv.split(',') if year})

            colors = []
            if colors_csv:
                colors = sorted({color for color in colors_csv.split(',') if color})

            cars.append({
                "name": name,
                "years": years,
                "colors": colors,
            })
        return cars