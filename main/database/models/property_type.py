from dataclasses import dataclass
from typing import Optional


@dataclass
class PropertyType:
    name: str
    description: Optional[str] = None
    id: Optional[int] = None
