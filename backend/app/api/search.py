# backend/app/api/search.py
from fastapi import APIRouter
from app.schemas.search import SearchRequest, SearchResponse
from app.services.searcher import CaseSearcher
from urllib.parse import urlparse

router = APIRouter(tags=["Search"])

@router.post("/search", response_model=SearchResponse)
async def search_cases(payload: SearchRequest):
    searcher = CaseSearcher()
    results = await searcher.search(payload.query, payload.limit)
    
    # Валидация URL перед отправкой на фронтенд
    valid_results = []
    for result in results:
        try:
            parsed = urlparse(result.url)
            if parsed.scheme in ('http', 'https') and parsed.netloc:
                valid_results.append(result)
        except:
            continue
    
    return SearchResponse(results=valid_results)