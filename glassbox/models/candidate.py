from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class EngineType(str, Enum):
    OPRO = "OPRO"
    APE = "APE"
    BREEDER = "BREEDER"
    S2A = "S2A"

class UnifiedCandidate(BaseModel):
    """
    The atomic unit of a 'Result' displayed in the GlassBox UI.
    Standardizes output across all optimization engines.
    """
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    engine_type: EngineType
    generation_index: int = Field(..., description="Step or generation number")
    
    # Content
    display_text: str = Field(..., description="Short text for List View (e.g. Prompt Snippet)")
    full_content: str = Field(..., description="Complete content for Detail View")
    output: Optional[str] = Field(default="", description="Primary output content for Result View")
    
    # Metrics
    score_aggregate: float = Field(..., description="Mean score from Test Bench (0-100)")
    test_results: Dict[str, float] = Field(
        default_factory=dict, 
        description="Individual test case scores, e.g. {'input_a': 90, 'input_b': 85}"
    )
    
    # Engine-Specific Metadata (Glass Box internals)
    meta: Dict[str, Any] = Field(default_factory=dict)
