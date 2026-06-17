from database.db_manager import get_connection


class ScrapeSessionRepository:
    def create(self, source: str, status: str = "running") -> int:
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO scrape_sessions (source, status) VALUES (?, ?)",
                (source, status),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def list_all(self):
        with get_connection() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM scrape_sessions ORDER BY session_id")]
