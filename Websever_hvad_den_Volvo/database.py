import sqlite3
from pathlib import Path

if __package__:
    from .car_data import VOLVO_DETAILS, VOLVO_MODELS
else:
    from car_data import VOLVO_DETAILS, VOLVO_MODELS


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "volvo.sqlite3"


def _connect(db_path=None):
    target = Path(db_path) if db_path else DEFAULT_DB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection, target


def initialize_database(db_path=None):
    connection, target = _connect(db_path)
    try:
        connection.executescript(
            """
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
        )
        connection.executemany(
            "INSERT OR IGNORE INTO car_models (name) VALUES (?)",
            ((model_name,) for model_name in VOLVO_MODELS),
        )
        for model_name, (years, colors) in VOLVO_DETAILS.items():
            model_id = connection.execute(
                "SELECT id FROM car_models WHERE name = ?", (model_name,)
            ).fetchone()["id"]
            for year in years:
                connection.execute(
                    "INSERT OR IGNORE INTO model_years (model_id, year) VALUES (?, ?)",
                    (model_id, year),
                )
            for color in colors:
                connection.execute("INSERT OR IGNORE INTO colors (name) VALUES (?)", (color,))
                color_id = connection.execute(
                    "SELECT id FROM colors WHERE name = ?", (color,)
                ).fetchone()["id"]
                connection.execute(
                    "INSERT OR IGNORE INTO model_colors (model_id, color_id) VALUES (?, ?)",
                    (model_id, color_id),
                )
        connection.commit()
    finally:
        connection.close()
    return str(target)


def ensure_database_exists(db_path=None):
    target = Path(db_path) if db_path else DEFAULT_DB_PATH
    if not target.exists():
        initialize_database(target)
        return

    connection = sqlite3.connect(target)
    try:
        table_exists = connection.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type = 'table' AND name = 'car_models'"
        ).fetchone()
    finally:
        connection.close()
    if table_exists is None:
        initialize_database(target)


def get_car_models(model_name=None, db_path=None):
    target = Path(db_path) if db_path else DEFAULT_DB_PATH
    ensure_database_exists(target)
    query = "SELECT id, name FROM car_models"
    parameters = ()
    if model_name is not None:
        query += " WHERE LOWER(name) = LOWER(?)"
        parameters = (model_name,)
    query += " ORDER BY name"

    connection = sqlite3.connect(target)
    try:
        rows = connection.execute(query, parameters).fetchall()
    finally:
        connection.close()
    cars = []
    connection = sqlite3.connect(target)
    try:
        for _, name in rows:
            colors = connection.execute(
                "SELECT c.name FROM colors c JOIN model_colors mc ON mc.color_id = c.id "
                "JOIN car_models cm ON cm.id = mc.model_id WHERE cm.name = ? ORDER BY c.name",
                (name,),
            ).fetchall()
            years = connection.execute(
                "SELECT year FROM model_years WHERE model_id = "
                "(SELECT id FROM car_models WHERE name = ?) ORDER BY year",
                (name,),
            ).fetchall()
            cars.append({
                "model": name,
                "name": name,
                "colors": [color[0] for color in colors],
                "years": [year[0] for year in years],
            })
    finally:
        connection.close()
    return cars
