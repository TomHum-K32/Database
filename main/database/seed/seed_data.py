from database.db_manager import initialize_db
from database.models.property import Property
from database.repositories.location_repository import LocationRepository
from database.repositories.price_history_repository import PriceHistoryRepository
from database.repositories.property_repository import PropertyRepository
from database.repositories.property_type_repository import PropertyTypeRepository


def seed_demo_data() -> None:
    initialize_db()

    location_repo = LocationRepository()
    type_repo = PropertyTypeRepository()
    property_repo = PropertyRepository()
    history_repo = PriceHistoryRepository()

    location_id = location_repo.create("Quận 7", "Quận 7", "Hồ Chí Minh")
    type_id = type_repo.create("Apartment", "Căn hộ hiện đại")

    property_id = property_repo.create(
        Property(
            title="Căn hộ Sunrise",
            address="123 Nguyễn Văn Linh",
            price=2500000000,
            bedrooms=2,
            bathrooms=2,
            area_sq_m=85,
            location_id=location_id,
            property_type_id=type_id,
        )
    )
    history_repo.create(property_id, 2500000000)
    history_repo.create(property_id, 2550000000)
