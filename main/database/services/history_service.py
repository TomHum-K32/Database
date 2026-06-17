"""
DB-05: History Service
Load and analyze historical data for property listings.
"""

from typing import List, Dict, Any, Optional
from database.repositories.price_history_repository import PriceHistoryRepository


class HistoryService:
    """Service for loading and analyzing property price history."""
    
    def __init__(self):
        """Initialize history service with repository."""
        self.repository = PriceHistoryRepository()
    
    def get_listing_history(self, property_id: int) -> List[Dict[str, Any]]:
        """
        Get formatted price history for a property.
        
        Process:
        1. Query price_history by property_id
        2. Sort by time (oldest to newest)
        3. Format each record as dictionary
        
        Args:
            property_id: The property ID to get history for
            
        Returns:
            List of dictionaries with history records:
            [
              {
                "history_id": 1,
                "property_id": 1,
                "price": 850000,
                "captured_at": "2026-06-01T10:30:00",
                "recorded_at": "2026-06-01T10:30:00"
              },
              ...
            ]
            
        Examples:
            >>> service = HistoryService()
            >>> history = service.get_listing_history(1)
            >>> len(history)
            3
            >>> history[0]["price"]
            850000
        """
        # Get raw records from repository
        records = self.repository.get_history_by_property(property_id)
        
        # Format as list of dictionaries
        history = []
        for record in records:
            # record is already a dict from repository (fetchall returns dict rows)
            data = {
                "history_id": record.get("history_id"),
                "property_id": record.get("property_id"),
                "price": record.get("price"),
                "captured_at": record.get("captured_at"),
                "recorded_at": record.get("recorded_at"),
                "session_id": record.get("session_id")
            }
            history.append(data)
        
        return history
    
    def get_average_price(self, property_id: int) -> Optional[float]:
        """
        Calculate average price across all history records.
        
        Args:
            property_id: The property ID
            
        Returns:
            Average price or None if no records
            
        Examples:
            >>> service = HistoryService()
            >>> avg = service.get_average_price(1)
            >>> avg
            820000.0
        """
        history = self.get_listing_history(property_id)
        
        if not history:
            return None
        
        total = sum(record["price"] for record in history)
        return total / len(history)
    
    def get_price_statistics(self, property_id: int) -> Dict[str, Any]:
        """
        Get comprehensive price statistics for a property.
        
        Returns:
            Dictionary with min, max, avg, count of price changes
            
        Examples:
            >>> stats = service.get_price_statistics(1)
            >>> stats["min_price"]
            790000
            >>> stats["max_price"]
            850000
            >>> stats["count"]
            3
        """
        history = self.get_listing_history(property_id)
        
        if not history:
            return {
                "property_id": property_id,
                "count": 0,
                "min_price": None,
                "max_price": None,
                "avg_price": None,
                "first_price": None,
                "last_price": None,
                "total_change": None
            }
        
        prices = [record["price"] for record in history]
        
        first_price = prices[0]
        last_price = prices[-1]
        total_change = last_price - first_price
        
        return {
            "property_id": property_id,
            "count": len(history),
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": sum(prices) / len(prices),
            "first_price": first_price,
            "last_price": last_price,
            "total_change": total_change,
            "change_percentage": (total_change / first_price * 100) if first_price else 0
        }
    
    def get_latest_price(self, property_id: int) -> Optional[float]:
        """
        Get the most recent price for a property.
        
        Args:
            property_id: The property ID
            
        Returns:
            Latest recorded price or None if no history
        """
        history = self.get_listing_history(property_id)
        
        if not history:
            return None
        
        # Last record is most recent (sorted by captured_at ASC)
        return history[-1]["price"]
    
    def get_price_trend(self, property_id: int) -> str:
        """
        Determine price trend: 'up', 'down', or 'stable'.
        
        Args:
            property_id: The property ID
            
        Returns:
            'up' if price increased, 'down' if decreased, 'stable' if unchanged,
            or 'no_data' if no history
        """
        stats = self.get_price_statistics(property_id)
        
        if stats["count"] < 2:
            return "no_data"
        
        change = stats["total_change"]
        
        if change > 0:
            return "up"
        elif change < 0:
            return "down"
        else:
            return "stable"
