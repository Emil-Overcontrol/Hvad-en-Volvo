import sqlite3
from pathlib import Path

if __package__:
    from .car_data import VOLVO_MODELS
else:
    from car_data import VOLVO_MODELS


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
    return [
        {"model": name, "name": name, "colors": [], "years": []}
        for _, name in rows
    ]
