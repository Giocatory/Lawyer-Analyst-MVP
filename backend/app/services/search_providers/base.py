from abc import ABC, abstractmethod
from typing import List
from app.schemas.search import SearchResult

class SearchProvider(ABC):

    @abstractmethod
    async def search(self, query: str, limit: int) -> List[SearchResult]:
        pass
