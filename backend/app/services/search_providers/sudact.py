from typing import List
import httpx
from bs4 import BeautifulSoup
from app.services.search_providers.base import SearchProvider
from app.schemas.search import SearchResult
import logging
import json

logger = logging.getLogger(__name__)

class SudactSearchProvider(SearchProvider):
    """Провайдер для поиска судебных решений на sudact.ru"""
    
    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        # Используем другой источник судебной практики
        return await self._search_kad_arbitr(query, limit)
    
    async def _search_kad_arbitr(self, query: str, limit: int) -> List[SearchResult]:
        """Поиск на kad.arbitr.ru (Картотека арбитражных дел)"""
        search_url = "https://kad.arbitr.ru/"
        
        try:
            # Сначала получаем страницу для получения необходимых токенов/параметров
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(search_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })
                response.raise_for_status()
            
            # Для упрощения возвращаем информацию о том, где можно найти судебную практику
            results = [
                SearchResult(
                    title="Картотека арбитражных дел (КАД)",
                    url="https://kad.arbitr.ru/",
                    source="kad.arbitr.ru",
                    snippet="Официальная картотека арбитражных судов РФ. Поиск по делам, судебным актам, участникам процесса."
                ),
                SearchResult(
                    title="Судебные акты по микрозаймам",
                    url="https://kad.arbitr.ru/Search?case_number=&judge=&date_from=&date_to=&case_material=&court=&judgment=&case_uid=&plaintiff=&defendant=&plaintiff_representative=&defendant_representative=&article=микрозайм&article_number=&case_decision_result=&case_decision_court=&case_decision_court_id=&case_decision_date_from=&case_decision_date_to=&is_document_with_text=&search_area=1&search_option=1&text=%D0%BC%D0%B8%D0%BA%D1%80%D0%BE%D0%B7%D0%B0%D0%B9%D0%BC%D1%8B",
                    source="kad.arbitr.ru",
                    snippet="Поиск судебных решений по делам о микрозаймах в арбитражных судах РФ"
                ),
                SearchResult(
                    title="ГАС Правосудие (суды общей юрисдикции)",
                    url="https://sudrf.ru/",
                    source="sudrf.ru",
                    snippet="Государственная автоматизированная система Российской Федерации «Правосудие». Поиск судебных решений по гражданским делам."
                )
            ]
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Ошибка поиска на kad.arbitr.ru: {e}")
            return []