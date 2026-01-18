from app.services.search_providers.base import SearchProvider
from app.schemas.search import SearchResult

class MockSearchProvider(SearchProvider):

    async def search(self, query: str, limit: int):
        return [
            SearchResult(
                title="Дело № А40-123456/2022",
                url="https://sudact.ru/mock/1",
                source="mock",
                snippet="Суд удовлетворил иск о неосновательном обогащении..."
            )
        ]
