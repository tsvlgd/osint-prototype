from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime, timezone
from typing import Dict, Any, Literal
from uuid import UUID, uuid4

class IntelligenceRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source_name: str
    retrieval_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_url: HttpUrl
    confidence: float = Field(ge=0.0, le=1.0)
    raw_data: Dict[str, Any]

class TargetInvestigation(BaseModel):
    """
    Represents the entire state of a single investigation.
    """
    target_query: str
    status: Literal["pending", "analyzing", "completed", "failed"] = "pending"
    records: list[IntelligenceRecord] = []
    
    def add_record(self, record: IntelligenceRecord):
        self.records.append(record)

