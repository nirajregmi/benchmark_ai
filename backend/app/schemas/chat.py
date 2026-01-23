from typing import List, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []
    selected_pods: Optional[List[str]] = []

class ChatResponse(BaseModel):
    response: str
