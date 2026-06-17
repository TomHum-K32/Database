from dataclasses import dataclass
from typing import Optional


@dataclass
class Property:
    title: str
    address: Optional[str] = None
    price: float = 0.0
    bedrooms: int = 0
    bathrooms: int = 0
    area_sq_m: float = 0.0
    location_id: Optional[int] = None
    property_type_id: Optional[int] = None
    id: Optional[int] = None
    external_id: str = ""
    description: Optional[str] = None
    current_price: Optional[float] = None
    area: float = 0.0
    listing_url: Optional[str] = None
    listing_date: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    type_id: Optional[int] = None
