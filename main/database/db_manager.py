import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


class DatabaseManager:
    """Small wrapper around the SQLite database used by the project."""

    def __init__(self, db_name: str = "database.db") -> None:
        self.db_name = Path(db_name)
        if not self.db_name.is_absolute():
            self.db_name = BASE_DIR / self.db_name

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_name)
        connection.row_factory = sqlite3.Row
        return connection

    def create_database(self) -> None:
        self.db_name.parent.mkdir(parents=True, exist_ok=True)
        self.db_name.touch(exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
            connection.commit()


def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite connection."""
    return DatabaseManager().connect()


def initialize_db() -> None:
    """Create the database file and apply schema."""
    DatabaseManager().create_database()


def reset_db() -> None:
    """Remove and recreate the database file."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    initialize_db()
