from typing import Optional, Dict, Any

class OrchestratorState:
    def __init__(
        self,
        user_id: int,
        conversation_id: str,
        user_input: str,
    ):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.user_input = user_input

        # Filled during flow
        self.intent: Optional[str] = None
        self.requires_db: bool = False
        self.parameters: Dict[str, Any] = {}

        self.db_result: Optional[Any] = None
        self.response: Optional[str] = None