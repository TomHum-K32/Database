from datetime import datetime

from database.models.property import Property
from database.repositories.location_repository import LocationRepository
from database.repositories.price_history_repository import PriceHistoryRepository
from database.repositories.property_repository import PropertyRepository
from database.repositories.property_type_repository import PropertyTypeRepository
from database.repositories.listing_repository import ListingRepository


class ListingService:
    def __init__(self) -> None:
        self.property_repo = PropertyRepository()
        self.listing_repo = ListingRepository()
        self.location_repo = LocationRepository()
        self.property_type_repo = PropertyTypeRepository()
        self.price_history_repo = PriceHistoryRepository()

    def create_listing(self, property_item: Property) -> int:
        property_id = self.property_repo.create(property_item)
        self.price_history_repo.create(property_id, property_item.current_price if property_item.current_price is not None else property_item.price)
        return property_id

    def save_scraped_listing(self, listing: dict) -> dict:
        existing = self.property_repo.get_by_external_id(listing["external_id"])

        if existing is None:
            property_id = self.property_repo.create(
                Property(
                    title=listing.get("title", "Untitled"),
                    external_id=listing["external_id"],
                    price=float(listing.get("price", 0)),
                    current_price=float(listing.get("price", 0)),
                    description=listing.get("description"),
                    listing_url=listing.get("listing_url"),
                    listing_date=listing.get("listing_date"),
                    first_seen=listing.get("first_seen") or datetime.utcnow().isoformat(),
                    last_seen=listing.get("last_seen") or datetime.utcnow().isoformat(),
                )
            )
            self.price_history_repo.add_price_record(property_id, None, float(listing.get("price", 0)))
            return {"status": "created", "property_id": property_id}

        current_price = float(existing.get("current_price") or existing.get("price") or 0)
        new_price = float(listing.get("price", current_price))

        if new_price != current_price:
            self.property_repo.update_property_price(existing["property_id"], new_price)
            self.price_history_repo.add_price_record(existing["property_id"], None, new_price)
            return {"status": "updated", "property_id": existing["property_id"]}

        self.property_repo.update_last_seen(existing["property_id"])
        return {"status": "unchanged", "property_id": existing["property_id"]}

    def get_listing_count(self) -> int:
        return self.property_repo.count()

    def update_existing_listing(self, external_id: str, new_listing_data: dict) -> dict:
        """Comprehensive listing update with field comparison.
        
        Process:
        1. Find existing listing by external_id
        2. If not found, create new listing
        3. If found, compare all relevant fields
        4. Update if changes detected
        5. Update last_seen timestamp
        
        Args:
            external_id: Unique identifier (e.g., 'REA001')
            new_listing_data: Dictionary with new listing data from scraper
            
        Returns:
            Dictionary with status, property_id, and changes made:
            - status: 'created', 'updated', or 'unchanged'
            - property_id: The property_id
            - changes: Dictionary of changed fields (if updated)
        """
        # Step 1: Check if listing exists
        existing = self.listing_repo.get_by_external_id(external_id)
        
        # Step 2: If not found, create new listing
        if existing is None:
            property_id = self.listing_repo.create(
                Property(
                    title=new_listing_data.get("title", "Untitled"),
                    external_id=external_id,
                    price=float(new_listing_data.get("price", 0)),
                    current_price=float(new_listing_data.get("price", 0)),
                    description=new_listing_data.get("description"),
                    listing_url=new_listing_data.get("listing_url"),
                    listing_date=new_listing_data.get("listing_date"),
                    first_seen=datetime.utcnow().isoformat(),
                    last_seen=datetime.utcnow().isoformat(),
                    area=float(new_listing_data.get("area", 0)),
                    area_sq_m=float(new_listing_data.get("area_sq_m", 0)),
                    bedrooms=int(new_listing_data.get("bedrooms", 0)),
                    bathrooms=int(new_listing_data.get("bathrooms", 0)),
                )
            )
            self.price_history_repo.add_price_record(
                property_id, None, float(new_listing_data.get("price", 0))
            )
            return {"status": "created", "property_id": property_id, "changes": {}}
        
        # Step 3: Compare fields for existing listing
        changes = self.listing_repo.compare_listings(existing, new_listing_data)
        
        # Step 4: Update if changes found
        if changes:
            self.listing_repo.update_listing(existing["property_id"], changes)
            
            # Track price changes in price history
            if "price" in changes or "current_price" in changes:
                new_price = changes.get("price") or changes.get("current_price")
                if new_price is not None:
                    self.price_history_repo.add_price_record(
                        existing["property_id"], None, float(new_price)
                    )
            
            return {"status": "updated", "property_id": existing["property_id"], "changes": changes}
        
        # Step 5: No changes, just update last_seen
        self.listing_repo.update_listing(existing["property_id"], {})
        return {"status": "unchanged", "property_id": existing["property_id"], "changes": {}}
