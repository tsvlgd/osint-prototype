# adapters/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.models import IntelligenceRecord

class BaseAdapter(ABC):
    def __init__(self):
        self.source_name = "Unknown"

    @abstractmethod
    async def fetch(self, query: str) -> List[Dict[str, Any]]:
        """Every adapter must implement this to return standardized data."""
        pass
    
    def normalize_record(self, raw_data: Any, confidence: float, url: str) -> IntelligenceRecord:
        """Helper to coerce raw data into our validated Pydantic model."""
        return IntelligenceRecord(
            source_name=self.source_name,
            source_url=url,
            confidence=confidence,
            raw_data=raw_data
        )