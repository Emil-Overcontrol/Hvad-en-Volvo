import os
import sqlite3
import tempfile
import unittest

from database import initialize_database, get_car_models


class DatabaseTests(unittest.TestCase):
    def test_initialize_database_creates_models(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "volvo.sqlite3")
            initialize_database(db_path)

            conn = sqlite3.connect(db_path)
            try:
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('car_models','model_years','colors','model_colors')"
                ).fetchall()
            finally:
                conn.close()
            self.assertEqual(len(tables), 4)

            models = get_car_models(db_path=db_path)
            self.assertIn("240", {model["name"] for model in models})
            self.assertIn("XC90", {model["name"] for model in models})


if __name__ == "__main__":
    unittest.main()
