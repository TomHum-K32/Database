import sqlite3
import unittest

from database.db_manager import reset_db
from database.repositories.location_repository import LocationRepository
from database.repositories.property_type_repository import PropertyTypeRepository


class TestDuplicates(unittest.TestCase):
    def setUp(self) -> None:
        reset_db()

    def test_duplicate_type_name_is_rejected(self) -> None:
        type_repo = PropertyTypeRepository()
        type_repo.create("Apartment")

        with self.assertRaises(sqlite3.IntegrityError):
            type_repo.create("Apartment")

    def test_duplicate_location_name_is_allowed(self) -> None:
        location_repo = LocationRepository()
        location_repo.create("District 1")
        location_repo.create("District 1")

        self.assertEqual(len(location_repo.list_all()), 2)


if __name__ == "__main__":
    unittest.main()
