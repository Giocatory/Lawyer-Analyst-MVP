import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse, parse_qs, unquote
from typing import List
from app.services.search_providers.base import SearchProvider
from app.services.search_providers.sudact import SudactSearchProvider
from app.schemas.search import SearchResult

class CaseSearcher:
    def __init__(self):
        # Инициализируем несколько провайдеров поиска
        self.providers = [
            SudactSearchProvider(),
            WebSearchProvider()
        ]
    
    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Выполняет поиск по нескольким источникам параллельно"""
        tasks = []
        results_per_provider = max(1, limit // len(self.providers))
        
        for provider in self.providers:
            tasks.append(provider.search(query, results_per_provider))
        
        # Выполняем все поиски параллельно
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Объединяем результаты
        all_results = []
        for results in results_lists:
            if isinstance(results, Exception):
                continue
            all_results.extend(results)
        
        # Удаляем дубликаты по URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results[:limit]

# backend/app/services/searcher.py
class WebSearchProvider(SearchProvider):
    """Провайдер для веб-поиска через DuckDuckGo"""
    
    async def search(self, query: str, limit: int) -> List[SearchResult]:
        # ИСПРАВЛЕНО: используем запрос пользователя напрямую
        search_query = f"{query} судебная практика россия"
        
        # Добавляем релевантные юридические термины для лучшего поиска
        legal_keywords = ["суд", "решение", "исковое заявление", "статья", "кодекс", "право"]
        has_legal_terms = any(term in query.lower() for term in legal_keywords)
        
        if not has_legal_terms:
            search_query += " закон статья решение суда"
        
        encoded_query = quote_plus(search_query)
        url = f"https://html.duckduckgo.com/html?q={encoded_query}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }

        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            # Извлекаем результаты
            for result in soup.select(".result")[:limit]:
                title_el = result.select_one(".result__a, a.result-title")
                snippet_el = result.select_one(".result__snippet")
                url_el = result.select_one("a")

                if not title_el or not url_el:
                    continue

                # Обрабатываем URL
                raw_link = url_el.get("href", "")
                real_link = self._extract_real_url(raw_link)

                title = title_el.get_text(strip=True)
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                source = self._extract_domain(real_link)

                results.append(SearchResult(
                    title=title,
                    url=real_link,
                    source=source,
                    snippet=snippet[:300] + "..." if len(snippet) > 300 else snippet
                ))

            return results
        except Exception as e:
            print(f"Ошибка веб-поиска: {e}")
            return []
    
    def _extract_real_url(self, url: str) -> str:
        """Извлекает реальный URL из редиректа DuckDuckGo"""
        # Обработка URL формата /l/?uddg=https%3A%2F%2Fexample.com...
        if url.startswith("/l/") or "duckduckgo.com/l/" in url:
            parsed = urlparse(url) if url.startswith("http") else urlparse(f"https://duckduckgo.com{url}")
            qs = parse_qs(parsed.query)
            
            if "uddg" in qs:
                decoded_url = unquote(qs["uddg"][0])
                # Удаляем возможные лишние параметры
                cleaned_url = decoded_url.split("&")[0]
                return cleaned_url
        
        # Обработка относительных путей
        if url.startswith("/"):
            return f"https://duckduckgo.com{url}"
        
        # Обработка URL без схемы
        if url.startswith("//"):
            return f"https:{url}"
        
        return url
    
    def _extract_domain(self, url: str) -> str:
        """Извлекает домен из URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Удаляем www. и другие поддомены для чистоты отображения
            if domain.startswith("www."):
                domain = domain[4:]
            return domain or "unknown"
        except:
            return "unknown"