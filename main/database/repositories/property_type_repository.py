from typing import Optional

from database.db_manager import get_connection


class PropertyTypeRepository:
    def create(self, name: str, description: Optional[str] = None) -> int:
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO property_types (name, description) VALUES (?, ?)",
                (name, description),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def list_all(self):
        with get_connection() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM property_types ORDER BY type_id")]
