from pydantic import BaseModel
from typing import List

class Document(BaseModel):
    title: str
    text: str

class AnalyzeRequest(BaseModel):
    query: str
    documents: List[Document]

class AnalyzeResponse(BaseModel):
    result: str
