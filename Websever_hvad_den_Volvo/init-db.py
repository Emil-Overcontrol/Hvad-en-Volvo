from database import DEFAULT_DB_PATH, initialize_database


if __name__ == "__main__":
    db_path = initialize_database()
    print(f"Volvo database created at {db_path}")
