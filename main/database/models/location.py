from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    name: str
    district: Optional[str] = None
    city: Optional[str] = None
    id: Optional[int] = None
