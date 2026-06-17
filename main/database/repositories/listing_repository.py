from datetime import datetime
from typing import Optional, Dict, Any

from database.db_manager import get_connection
from database.models.property import Property


class ListingRepository:
    """Repository for managing property listings with focus on external_id matching."""
    
    def get_by_external_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Find listing by external_id (unique identifier for each listing).
        
        Args:
            external_id: The external ID from scraper (e.g., 'REA001')
            
        Returns:
            Dictionary with listing data if found, None otherwise
        """
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM properties WHERE external_id = ?",
                (external_id,),
            ).fetchone()
            return dict(row) if row else None
    
    def create(self, listing_data: Property) -> int:
        """Insert a new listing into database.
        
        Args:
            listing_data: Property object with listing details
            
        Returns:
            property_id of the newly created listing
        """
        current_price = listing_data.current_price if listing_data.current_price is not None else listing_data.price
        external_id = listing_data.external_id or f"PROP-{int(datetime.utcnow().timestamp() * 1000)}"
        description = listing_data.description or listing_data.address
        area = listing_data.area if listing_data.area else listing_data.area_sq_m
        type_id = listing_data.type_id if listing_data.type_id is not None else listing_data.property_type_id
        
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
                    listing_data.title,
                    description,
                    current_price,
                    area,
                    listing_data.bedrooms,
                    listing_data.bathrooms,
                    listing_data.listing_url,
                    listing_data.listing_date,
                    listing_data.first_seen or datetime.utcnow().isoformat(),
                    listing_data.last_seen or datetime.utcnow().isoformat(),
                    type_id,
                    listing_data.location_id,
                    listing_data.address,
                    listing_data.price,
                    listing_data.area_sq_m,
                    listing_data.property_type_id,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)
    
    def update_listing(self, property_id: int, updates: Dict[str, Any]) -> None:
        """Update listing fields and last_seen timestamp.
        
        Args:
            property_id: The property_id to update
            updates: Dictionary of fields to update (e.g., {'price': 820000, 'area': 75})
        """
        updates['last_seen'] = datetime.utcnow().isoformat()
        
        # Build dynamic UPDATE query
        set_clauses = [f"{key} = ?" for key in updates.keys()]
        set_clause = ", ".join(set_clauses)
        values = list(updates.values()) + [property_id]
        
        with get_connection() as connection:
            connection.execute(
                f"UPDATE properties SET {set_clause} WHERE property_id = ?",
                values,
            )
            connection.commit()
    
    def get_fields_to_check(self) -> list:
        """Return list of fields to check for changes.
        
        Returns:
            List of field names that should be monitored for changes
        """
        return ['price', 'current_price', 'area', 'area_sq_m', 'bedrooms', 'bathrooms', 'description']
    
    def compare_listings(self, old_listing: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare old and new listing data to find changes.
        
        Args:
            old_listing: Existing listing data from database
            new_data: New listing data from scraper
            
        Returns:
            Dictionary with changed fields: {'field_name': new_value, ...}
            Empty dict if no changes
        """
        changes = {}
        fields_to_check = self.get_fields_to_check()
        
        for field in fields_to_check:
            old_value = old_listing.get(field)
            new_value = new_data.get(field)
            
            # Handle numeric comparisons
            if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                if float(old_value or 0) != float(new_value or 0):
                    changes[field] = new_value
            # Handle text comparisons
            elif str(old_value or "") != str(new_value or ""):
                changes[field] = new_value
        
        return changes
    
    def count(self) -> int:
        """Get total count of listings in database."""
        with get_connection() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM properties").fetchone()[0])
    
    def list_all(self):
        """Get all listings."""
        with get_connection() as connection:
            rows = connection.execute("SELECT * FROM properties ORDER BY property_id").fetchall()
            return [dict(row) for row in rows]
