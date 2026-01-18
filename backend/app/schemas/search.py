from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SearchResult(BaseModel):
    title: str
    url: str
    source: str
    snippet: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
