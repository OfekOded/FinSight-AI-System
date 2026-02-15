# agent_model.py - שומר את היסטוריית השיחה (רשימת הודעות משתמש והודעות בוט) כדי להציג אותה ברצף.
from dataclasses import dataclass

@dataclass
class AgentModel:
    current_question: str = ""