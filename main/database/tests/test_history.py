import unittest

from database.db_manager import reset_db
from database.models.property import Property
from database.repositories.price_history_repository import PriceHistoryRepository
from database.repositories.property_repository import PropertyRepository


class TestHistory(unittest.TestCase):
    def setUp(self) -> None:
        reset_db()

    def test_history_records_are_stored(self) -> None:
        property_repo = PropertyRepository()
        history_repo = PriceHistoryRepository()

        property_id = property_repo.create(Property(title="History House", address="2 Main", price=2000000))
        history_id = history_repo.create(property_id, 2100000)

        self.assertGreater(history_id, 0)


if __name__ == "__main__":
    unittest.main()
