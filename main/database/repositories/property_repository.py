from datetime import datetime

from database.db_manager import get_connection
from database.models.property import Property


class PropertyRepository:
    def create(self, property_item: Property) -> int:
        current_price = property_item.current_price if property_item.current_price is not None else property_item.price
        external_id = property_item.external_id or f"PROP-{int(datetime.utcnow().timestamp() * 1000)}"
        description = property_item.description or property_item.address
        area = property_item.area if property_item.area else property_item.area_sq_m
        type_id = property_item.type_id if property_item.type_id is not None else property_item.property_type_id

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO properties (
                    external_id, title, description, current_price, area, bedrooms, bathrooms,
                    listing_url, listing_date, first_seen, last_seen, type_id, location_id,
                    address, price, area_sq_m, property_type_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    external_id,
                    property_item.title,
                    description,
                    current_price,
                    area,
                    property_item.bedrooms,
                    property_item.bathrooms,
                    property_item.listing_url,
                    property_item.listing_date,
                    property_item.first_seen or datetime.utcnow().isoformat(),
                    property_item.last_seen,
                    type_id,
                    property_item.location_id,
                    property_item.address,
                    property_item.price,
                    property_item.area_sq_m,
                    property_item.property_type_id,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def get_by_external_id(self, external_id: str):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM properties WHERE external_id = ?",
                (external_id,),
            ).fetchone()
            return dict(row) if row else None

    def update_property_price(self, property_id: int, new_price: float) -> None:
        with get_connection() as connection:
            connection.execute(
                "UPDATE properties SET current_price = ?, price = ?, last_seen = ? WHERE property_id = ?",
                (new_price, new_price, datetime.utcnow().isoformat(), property_id),
            )
            connection.commit()

    def update_last_seen(self, property_id: int) -> None:
        with get_connection() as connection:
            connection.execute(
                "UPDATE properties SET last_seen = ? WHERE property_id = ?",
                (datetime.utcnow().isoformat(), property_id),
            )
            connection.commit()

    def delete_property(self, property_id: int) -> None:
        with get_connection() as connection:
            connection.execute("DELETE FROM properties WHERE property_id = ?", (property_id,))
            connection.commit()

    def list_all(self):
        with get_connection() as connection:
            rows = connection.execute("SELECT * FROM properties ORDER BY property_id").fetchall()
            return [dict(row) for row in rows]

    def count(self) -> int:
        with get_connection() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM properties").fetchone()[0])
