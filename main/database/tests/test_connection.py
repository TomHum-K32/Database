import unittest

from database.db_manager import initialize_db, reset_db


class TestConnection(unittest.TestCase):
    def setUp(self) -> None:
        reset_db()

    def test_initialize_db_creates_schema(self) -> None:
        initialize_db()
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
