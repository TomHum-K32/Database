import unittest

from database.db_manager import reset_db
from database.models.property import Property
from database.repositories.property_repository import PropertyRepository


class TestProperty(unittest.TestCase):
    def setUp(self) -> None:
        reset_db()

    def test_property_insert_and_count(self) -> None:
        repo = PropertyRepository()
        property_id = repo.create(Property(title="Test House", address="1 Main", price=1000000))

        self.assertGreater(property_id, 0)
        self.assertEqual(repo.count(), 1)


if __name__ == "__main__":
    unittest.main()
