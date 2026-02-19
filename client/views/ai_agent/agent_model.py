from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class AgentModel:
    current_question: str = ""
    history: List[Dict[str, str]] = field(default_factory=list)