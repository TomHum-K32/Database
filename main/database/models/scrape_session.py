from dataclasses import dataclass
from typing import Optional


@dataclass
class ScrapeSession:
    source: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    status: str = "running"
    id: Optional[int] = None
