from pydantic import BaseModel


class ClarifyRequest(BaseModel):
    query: str


class ClarifyResponse(BaseModel):
    explanation: str
