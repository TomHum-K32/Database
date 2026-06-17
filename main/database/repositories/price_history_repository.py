from datetime import datetime

from database.db_manager import get_connection


class PriceHistoryRepository:
    def create(self, property_id: int, price: float, session_id: int = None) -> int:
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO price_history (property_id, session_id, price, captured_at) VALUES (?, ?, ?, ?)",
                (property_id, session_id, price, datetime.utcnow().isoformat()),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def add_price_record(self, property_id: int, session_id: int = None, price: float = None) -> int:
        return self.create(property_id, price, session_id)

    def get_history_by_property(self, property_id: int):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM price_history WHERE property_id = ? ORDER BY captured_at, history_id",
                (property_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def list_all(self):
        with get_connection() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM price_history ORDER BY history_id")]
