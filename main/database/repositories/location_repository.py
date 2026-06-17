from typing import Optional

from database.db_manager import get_connection


class LocationRepository:
    def create(self, name: str, district: Optional[str] = None, city: Optional[str] = None) -> int:
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO locations (name, district, city) VALUES (?, ?, ?)",
                (name, district, city),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def list_all(self):
        with get_connection() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM locations ORDER BY location_id")]
