from pydantic import BaseModel, Field
from typing import Optional

class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict
    dangerous: bool = False
    requires_auth: bool = False

class AgentSpec(BaseModel):
    system_prompt: str
    tools: list[ToolSpec] = Field(default_factory=list)
    memory_enabled: bool = False
    memory_backend: Optional[str] = None
    max_turns: int = 10
    delegation_targets: list[str] = Field(default_factory=list)
