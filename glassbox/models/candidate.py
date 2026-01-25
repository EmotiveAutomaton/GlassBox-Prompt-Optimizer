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

    def get_diff(self, anchor: 'UnifiedCandidate') -> str:
        """
        Generate HTML diff comparing this candidate (Primary) against an Anchor.
        Uses difflib.SequenceMatcher for character/token level precision.
        """
        import difflib
        
        # We diff the full_content
        a_text = anchor.full_content
        b_text = self.full_content
        
        matcher = difflib.SequenceMatcher(None, a_text, b_text)
        html_parts = []
        
        for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
            if opcode == 'equal':
                html_parts.append(a_text[a0:a1])
            elif opcode == 'insert':
                # Green Background, 20% Opacity (#20C20E -> rgba(32, 194, 14, 0.2))
                html_parts.append(f'<span class="diff-add">{b_text[b0:b1]}</span>')
            elif opcode == 'delete':
                # Red Background, 20% Opacity + Strikethrough (#D9534F -> rgba(217, 83, 79, 0.2))
                html_parts.append(f'<span class="diff-del">{a_text[a0:a1]}</span>')
            elif opcode == 'replace':
                html_parts.append(f'<span class="diff-del">{a_text[a0:a1]}</span>')
                html_parts.append(f'<span class="diff-add">{b_text[b0:b1]}</span>')
                
        return "".join(html_parts)
