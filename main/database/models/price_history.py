from dataclasses import dataclass
from typing import Optional


@dataclass
class PriceHistory:
    property_id: int
    price: float
    recorded_at: Optional[str] = None
    id: Optional[int] = None
