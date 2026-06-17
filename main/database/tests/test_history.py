"""
DB-05: Test Historical Data Loading

Tests for price history retrieval and analysis:
- Load historical data by property ID
- Verify sorting by time
- Test empty history
- Calculate average prices
- Analyze price trends
"""

import unittest
from datetime import datetime, timedelta

from database.db_manager import reset_db
from database.models.property import Property
from database.repositories.price_history_repository import PriceHistoryRepository
from database.repositories.property_repository import PropertyRepository
from database.services.history_service import HistoryService


class TestHistory(unittest.TestCase):
    """Test suite for DB-05: Historical Data Loading."""
    
    def setUp(self) -> None:
        """Reset database before each test."""
        reset_db()
        self.property_repo = PropertyRepository()
        self.history_repo = PriceHistoryRepository()
        self.history_service = HistoryService()

    def test_01_history_records_are_stored(self) -> None:
        """Test: Basic history record insertion."""
        print("\n" + "="*60)
        print("TEST 1: History Records Are Stored")
        print("="*60)
        
        property_id = self.property_repo.create(
            Property(title="History House", address="2 Main", price=2000000)
        )
        history_id = self.history_repo.create(property_id, 2100000)

        self.assertGreater(history_id, 0, "history_id should be > 0")
        print(f"✓ Created history record: history_id={history_id}")

    def test_02_load_history_with_records(self) -> None:
        """
        Test 1: Get history for property with records.
        
        Expected:
        - Insert property
        - Insert 2 price records
        - Retrieve history should return 2 records
        - Records sorted by time
        """
        print("\n" + "="*60)
        print("TEST 2: Load History With Records")
        print("="*60)
        
        # Insert property
        property_id = self.property_repo.create(
            Property(
                title="Apartment CBD",
                address="123 Main St",
                price=850000
            )
        )
        print(f"✓ Created property: property_id={property_id}")
        
        # Insert first price: 850000
        h1 = self.history_repo.create(property_id, 850000)
        print(f"✓ Price 1: 850000 (history_id={h1})")
        
        # Insert second price: 820000
        h2 = self.history_repo.create(property_id, 820000)
        print(f"✓ Price 2: 820000 (history_id={h2})")
        
        # Insert third price: 790000
        h3 = self.history_repo.create(property_id, 790000)
        print(f"✓ Price 3: 790000 (history_id={h3})")
        
        # Load history via service
        history = self.history_service.get_listing_history(property_id)
        
        # Assertions
        self.assertEqual(len(history), 3, "Should have 3 records")
        print(f"✓ Retrieved {len(history)} history records")
        
        # Verify sorting (oldest to newest)
        self.assertEqual(history[0]["price"], 850000, "First should be 850000")
        self.assertEqual(history[1]["price"], 820000, "Second should be 820000")
        self.assertEqual(history[2]["price"], 790000, "Third should be 790000")
        print("✓ Records sorted by time (oldest first)")
        
        # Verify property_id matches
        for record in history:
            self.assertEqual(record["property_id"], property_id)
        print("✓ All records have correct property_id")

    def test_03_load_history_no_records(self) -> None:
        """
        Test 2: Get history for property with NO records.
        
        Expected:
        - Get history for non-existent property
        - Should return empty list
        """
        print("\n" + "="*60)
        print("TEST 3: Load History With No Records")
        print("="*60)
        
        # Try to get history for non-existent property
        history = self.history_service.get_listing_history(999)
        
        # Assertions
        self.assertEqual(len(history), 0, "Should return empty list")
        self.assertEqual(history, [], "Should be empty list")
        print("✓ Empty history returns empty list")

    def test_04_history_sorting_by_time(self) -> None:
        """
        Test 3: Verify records sorted by captured_at timestamp.
        
        Expected:
        - Insert prices in random order
        - Retrieve should be sorted by time
        """
        print("\n" + "="*60)
        print("TEST 4: History Sorting By Time")
        print("="*60)
        
        property_id = self.property_repo.create(
            Property(title="Sorted Property", address="456 Oak", price=1000000)
        )
        
        # Insert prices
        prices = [850000, 790000, 820000]  # Not in order
        for price in prices:
            self.history_repo.create(property_id, price)
        
        # Get history
        history = self.history_service.get_listing_history(property_id)
        
        # Verify sorting
        self.assertEqual(len(history), 3)
        print(f"✓ Retrieved {len(history)} records")
        
        # Check captured_at is sorted (should be in order of insertion)
        for i in range(len(history) - 1):
            current = history[i]["captured_at"]
            next_item = history[i + 1]["captured_at"]
            self.assertLessEqual(current, next_item, "Should be sorted by time")
        
        print("✓ All records sorted by captured_at (oldest first)")

    def test_05_average_price_calculation(self) -> None:
        """
        Test: Calculate average price from history.
        
        Expected:
        - 3 prices: 850000, 820000, 790000
        - Average: 820000
        """
        print("\n" + "="*60)
        print("TEST 5: Average Price Calculation")
        print("="*60)
        
        property_id = self.property_repo.create(
            Property(title="Average Test", address="789 Elm", price=850000)
        )
        
        # Insert prices
        prices = [850000, 820000, 790000]
        for price in prices:
            self.history_repo.create(property_id, price)
        
        # Calculate average via service
        avg = self.history_service.get_average_price(property_id)
        expected_avg = sum(prices) / len(prices)
        
        # Assertions
        self.assertIsNotNone(avg, "Average should not be None")
        self.assertEqual(avg, expected_avg, f"Average should be {expected_avg}")
        self.assertEqual(avg, 820000.0, "Average should be 820000")
        print(f"✓ Calculated average price: {avg}")

    def test_06_average_price_no_history(self) -> None:
        """Test: Average price with no history returns None."""
        print("\n" + "="*60)
        print("TEST 6: Average Price With No History")
        print("="*60)
        
        avg = self.history_service.get_average_price(999)
        
        self.assertIsNone(avg, "Should return None for non-existent property")
        print("✓ No history returns None")

    def test_07_price_statistics(self) -> None:
        """
        Test: Get comprehensive price statistics.
        
        Expected stats:
        - min, max, avg, first, last, total_change
        """
        print("\n" + "="*60)
        print("TEST 7: Price Statistics")
        print("="*60)
        
        property_id = self.property_repo.create(
            Property(title="Stats Property", address="321 Pine", price=850000)
        )
        
        # Insert prices: 850000 → 820000 → 790000
        prices = [850000, 820000, 790000]
        for price in prices:
            self.history_repo.create(property_id, price)
        
        # Get statistics
        stats = self.history_service.get_price_statistics(property_id)
        
        # Assertions
        self.assertEqual(stats["count"], 3, "Count should be 3")
        self.assertEqual(stats["min_price"], 790000, "Min should be 790000")
        self.assertEqual(stats["max_price"], 850000, "Max should be 850000")
        self.assertEqual(stats["avg_price"], 820000.0, "Avg should be 820000")
        self.assertEqual(stats["first_price"], 850000, "First should be 850000")
        self.assertEqual(stats["last_price"], 790000, "Last should be 790000")
        self.assertEqual(stats["total_change"], -60000, "Change should be -60000")
        
        print(f"✓ Statistics:")
        print(f"  - Count: {stats['count']}")
        print(f"  - Min: {stats['min_price']}")
        print(f"  - Max: {stats['max_price']}")
        print(f"  - Avg: {stats['avg_price']}")
        print(f"  - First: {stats['first_price']}")
        print(f"  - Last: {stats['last_price']}")
        print(f"  - Total change: {stats['total_change']}")
        print(f"  - Change %: {stats['change_percentage']:.2f}%")

    def test_08_price_trend_detection(self) -> None:
        """
        Test: Detect price trend (up/down/stable).
        
        Scenarios:
        - Price going down: 'down'
        - Price going up: 'up'
        - Price unchanged: 'stable'
        - No data: 'no_data'
        """
        print("\n" + "="*60)
        print("TEST 8: Price Trend Detection")
        print("="*60)
        
        # Test 1: Price going down
        p1 = self.property_repo.create(
            Property(title="Downtrend", address="Addr1", price=1000000)
        )
        self.history_repo.create(p1, 1000000)
        self.history_repo.create(p1, 900000)
        trend_down = self.history_service.get_price_trend(p1)
        self.assertEqual(trend_down, "down")
        print(f"✓ Downtrend: {trend_down}")
        
        # Test 2: Price going up
        p2 = self.property_repo.create(
            Property(title="Uptrend", address="Addr2", price=900000)
        )
        self.history_repo.create(p2, 900000)
        self.history_repo.create(p2, 1000000)
        trend_up = self.history_service.get_price_trend(p2)
        self.assertEqual(trend_up, "up")
        print(f"✓ Uptrend: {trend_up}")
        
        # Test 3: Price stable
        p3 = self.property_repo.create(
            Property(title="Stable", address="Addr3", price=500000)
        )
        self.history_repo.create(p3, 500000)
        self.history_repo.create(p3, 500000)
        trend_stable = self.history_service.get_price_trend(p3)
        self.assertEqual(trend_stable, "stable")
        print(f"✓ Stable trend: {trend_stable}")
        
        # Test 4: No data
        trend_none = self.history_service.get_price_trend(999)
        self.assertEqual(trend_none, "no_data")
        print(f"✓ No data: {trend_none}")

    def test_09_no_duplicates_in_history(self) -> None:
        """
        Test: Verify multiple updates don't create duplicate history entries.
        
        Scenario:
        - Initial property
        - Update 1: Create history record
        - Update 2: Create another history record
        - Should have 2 records, not more
        """
        print("\n" + "="*60)
        print("TEST 9: No Duplicates In History")
        print("="*60)
        
        property_id = self.property_repo.create(
            Property(title="No Dup Test", address="NoDup Lane", price=1000000)
        )
        print(f"✓ Created property: {property_id}")
        
        # Make 5 updates
        for i in range(5):
            price = 1000000 - (i * 10000)
            self.history_repo.create(property_id, price)
        
        # Get history
        history = self.history_service.get_listing_history(property_id)
        
        # Should have exactly 5 records
        self.assertEqual(len(history), 5, "Should have 5 records, not duplicates")
        print(f"✓ After 5 updates: {len(history)} records (no duplicates)")
        
        # Verify all prices are unique (descending)
        prices = [r["price"] for r in history]
        self.assertEqual(len(set(prices)), 5, "Should have 5 unique prices")
        print(f"✓ All 5 prices unique: {prices}")


if __name__ == "__main__":
    unittest.main()
