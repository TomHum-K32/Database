"""
Test DB-04: Update Existing Listings

This test suite demonstrates the complete workflow for handling property listings:
1. Initial insert of a new listing
2. Update when listing data changes
3. Verify no duplicates are created during updates
"""

import sqlite3
import unittest
from datetime import datetime
from pathlib import Path

from database.models.property import Property
from database.services.listing_service import ListingService
from database.repositories.listing_repository import ListingRepository
from database.db_manager import get_connection


class TestUpdateListing(unittest.TestCase):
    """Test suite for listing updates using external_id matching."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        self.listing_service = ListingService()
        self.listing_repo = ListingRepository()
        self.initial_count = self.listing_repo.count()
    
    def tearDown(self):
        """Clean up after each test."""
        # Delete test listings to keep database clean
        with get_connection() as connection:
            connection.execute("DELETE FROM properties WHERE external_id LIKE 'TEST%'")
            connection.commit()
    
    def test_01_initial_insert_new_listing(self):
        """Test 1: Insert initial listing with price 850000 and area 75."""
        
        print("\n" + "="*60)
        print("TEST 1: Initial Insert")
        print("="*60)
        
        # Initial state
        count_before = self.listing_repo.count()
        print(f"Listings before: {count_before}")
        
        # Insert listing: REA001 with price=850000, area=75
        result = self.listing_service.update_existing_listing(
            external_id="TEST_REA001",
            new_listing_data={
                "title": "Beautiful Apartment",
                "price": 850000,
                "area": 75,
                "bedrooms": 2,
                "bathrooms": 1,
                "description": "Spacious apartment in city center",
                "listing_url": "https://example.com/rea001"
            }
        )
        
        # Verify
        self.assertEqual(result["status"], "created", "Status should be 'created'")
        property_id = result["property_id"]
        self.assertIsNotNone(property_id, "property_id should be assigned")
        
        # Check database
        listing = self.listing_repo.get_by_external_id("TEST_REA001")
        self.assertIsNotNone(listing, "Listing should exist in database")
        self.assertEqual(listing["price"], 850000, "Price should be 850000")
        self.assertEqual(listing["area"], 75, "Area should be 75")
        self.assertEqual(listing["bedrooms"], 2, "Bedrooms should be 2")
        
        count_after = self.listing_repo.count()
        self.assertEqual(count_after, count_before + 1, "Count should increase by 1")
        
        print(f"✓ Listing created with property_id={property_id}")
        print(f"✓ external_id: TEST_REA001")
        print(f"✓ price: {listing['price']}")
        print(f"✓ area: {listing['area']}")
        print(f"✓ Total listings after: {count_after}")
    
    def test_02_update_when_price_changes(self):
        """Test 2: Update when price changes from 850000 to 820000."""
        
        print("\n" + "="*60)
        print("TEST 2: Update When Price Changes")
        print("="*60)
        
        # Step 1: Initial insert
        result1 = self.listing_service.update_existing_listing(
            external_id="TEST_REA002",
            new_listing_data={
                "title": "Property Two",
                "price": 850000,
                "area": 75,
                "bedrooms": 2,
                "bathrooms": 1,
                "description": "Initial description"
            }
        )
        
        property_id = result1["property_id"]
        self.assertEqual(result1["status"], "created")
        print(f"✓ Initial listing created: price=850000")
        
        # Verify database before update
        listing_before = self.listing_repo.get_by_external_id("TEST_REA002")
        print(f"✓ Before update: price={listing_before['price']}")
        
        # Step 2: Scraper finds same listing with updated price: 820000
        result2 = self.listing_service.update_existing_listing(
            external_id="TEST_REA002",
            new_listing_data={
                "title": "Property Two",
                "price": 820000,  # PRICE CHANGED
                "area": 75,       # unchanged
                "bedrooms": 2,
                "bathrooms": 1,
                "description": "Initial description"
            }
        )
        
        # Verify update status
        self.assertEqual(result2["status"], "updated", "Status should be 'updated'")
        self.assertEqual(result2["property_id"], property_id, "property_id should match")
        self.assertIn("price", result2["changes"], "price should be in changes")
        self.assertEqual(result2["changes"]["price"], 820000, "Updated price should be 820000")
        
        print(f"✓ Update detected and applied")
        print(f"✓ Changes: {result2['changes']}")
        
        # Verify database after update
        listing_after = self.listing_repo.get_by_external_id("TEST_REA002")
        self.assertEqual(listing_after["price"], 820000, "Price should be updated to 820000")
        
        print(f"✓ After update: price={listing_after['price']}")
    
    def test_03_no_duplicate_created(self):
        """Test 3: Verify no duplicate records created during update."""
        
        print("\n" + "="*60)
        print("TEST 3: No Duplicates Created")
        print("="*60)
        
        # Initial state
        count_before = self.listing_repo.count()
        print(f"Total listings before: {count_before}")
        
        # Insert listing
        result1 = self.listing_service.update_existing_listing(
            external_id="TEST_REA003",
            new_listing_data={
                "title": "Unique Property",
                "price": 500000,
                "area": 50,
                "bedrooms": 1,
                "bathrooms": 1,
                "description": "Test listing"
            }
        )
        
        count_after_insert = self.listing_repo.count()
        self.assertEqual(count_after_insert, count_before + 1, "Should have 1 new listing")
        print(f"✓ After insert: {count_after_insert} listings (inserted 1 new)")
        
        # Update the same listing multiple times
        for i in range(3):
            result = self.listing_service.update_existing_listing(
                external_id="TEST_REA003",
                new_listing_data={
                    "title": "Unique Property",
                    "price": 500000 + (i * 10000),  # Price changes each iteration
                    "area": 50,
                    "bedrooms": 1,
                    "bathrooms": 1,
                    "description": "Test listing"
                }
            )
            print(f"  Update {i+1}: price={500000 + (i * 10000)}, status={result['status']}")
        
        # Verify no duplicates
        count_after_updates = self.listing_repo.count()
        self.assertEqual(count_after_updates, count_after_insert, 
                        "Total count should not increase during updates")
        
        print(f"✓ After 3 updates: {count_after_updates} listings (still only 1)")
        print(f"✓ No duplicates created ✓")
        
        # Verify final listing has latest price
        listing_final = self.listing_repo.get_by_external_id("TEST_REA003")
        expected_price = 500000 + (2 * 10000)
        self.assertEqual(listing_final["price"], expected_price, 
                        f"Final price should be {expected_price}")
        print(f"✓ Final price: {listing_final['price']}")
    
    def test_04_all_field_comparisons(self):
        """Test 4: Verify all fields are compared correctly."""
        
        print("\n" + "="*60)
        print("TEST 4: Field Comparison Accuracy")
        print("="*60)
        
        # Insert initial listing
        self.listing_service.update_existing_listing(
            external_id="TEST_REA004",
            new_listing_data={
                "title": "Comparison Test",
                "price": 600000,
                "area": 80,
                "bedrooms": 3,
                "bathrooms": 2,
                "description": "Original description"
            }
        )
        
        print("✓ Initial listing inserted")
        
        # Test 1: Price change only
        result = self.listing_service.update_existing_listing(
            external_id="TEST_REA004",
            new_listing_data={
                "title": "Comparison Test",
                "price": 610000,  # Changed
                "area": 80,
                "bedrooms": 3,
                "bathrooms": 2,
                "description": "Original description"
            }
        )
        self.assertEqual(result["status"], "updated")
        self.assertIn("price", result["changes"])
        print("✓ Price change detected")
        
        # Test 2: Area change only
        result = self.listing_service.update_existing_listing(
            external_id="TEST_REA004",
            new_listing_data={
                "title": "Comparison Test",
                "price": 610000,
                "area": 85,  # Changed
                "bedrooms": 3,
                "bathrooms": 2,
                "description": "Original description"
            }
        )
        self.assertEqual(result["status"], "updated")
        self.assertIn("area", result["changes"])
        print("✓ Area change detected")
        
        # Test 3: Description change only
        result = self.listing_service.update_existing_listing(
            external_id="TEST_REA004",
            new_listing_data={
                "title": "Comparison Test",
                "price": 610000,
                "area": 85,
                "bedrooms": 3,
                "bathrooms": 2,
                "description": "Updated description"  # Changed
            }
        )
        self.assertEqual(result["status"], "updated")
        self.assertIn("description", result["changes"])
        print("✓ Description change detected")
        
        # Test 4: No changes
        result = self.listing_service.update_existing_listing(
            external_id="TEST_REA004",
            new_listing_data={
                "title": "Comparison Test",
                "price": 610000,
                "area": 85,
                "bedrooms": 3,
                "bathrooms": 2,
                "description": "Updated description"
            }
        )
        self.assertEqual(result["status"], "unchanged")
        print("✓ No changes detected correctly")
    
    def test_05_last_seen_updated(self):
        """Test 5: Verify last_seen timestamp is updated."""
        
        print("\n" + "="*60)
        print("TEST 5: Last Seen Timestamp")
        print("="*60)
        
        # Insert listing
        result = self.listing_service.update_existing_listing(
            external_id="TEST_REA005",
            new_listing_data={
                "title": "Timestamp Test",
                "price": 700000,
                "area": 100
            }
        )
        
        property_id = result["property_id"]
        listing_1 = self.listing_repo.get_by_external_id("TEST_REA005")
        first_last_seen = listing_1["last_seen"]
        print(f"✓ First last_seen: {first_last_seen}")
        
        # Wait a tiny bit and update
        import time
        time.sleep(1)
        
        # Update (unchanged) to trigger last_seen update
        result = self.listing_service.update_existing_listing(
            external_id="TEST_REA005",
            new_listing_data={
                "title": "Timestamp Test",
                "price": 700000,
                "area": 100
            }
        )
        
        listing_2 = self.listing_repo.get_by_external_id("TEST_REA005")
        second_last_seen = listing_2["last_seen"]
        print(f"✓ Second last_seen: {second_last_seen}")
        
        # Verify timestamp was updated
        self.assertGreater(second_last_seen, first_last_seen, 
                          "last_seen should be updated to more recent time")
        print("✓ last_seen timestamp updated correctly")


if __name__ == "__main__":
    unittest.main(verbosity=2)
