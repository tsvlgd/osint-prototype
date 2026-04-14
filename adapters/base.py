from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.models import IntelligenceRecord

class BaseAdapter(ABC):
    """
    The blueprint for all OSINT adapters.
    """
    def __init__(self):
        self.source_name = "Unknown"

    @abstractmethod
    async def fetch(self, query: str) -> List[Dict[str, Any]]:
        """
        Takes a target name/domain, queries the external source, 
        and returns a list of standardized dictionaries.
        """
        pass
    
    def normalize_record(self, raw_data: Any, confidence: float, url: str) -> IntelligenceRecord:
    return IntelligenceRecord(
        source_name=self.source_name,
        source_url=url,
        confidence=confidence,
        raw_data=raw_data
    )