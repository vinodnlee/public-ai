from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=1, max_length=128)


class ChatInitResponse(BaseModel):
    session_id: str
    stream_url: str
