import httpx
import os
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.is_configured = settings.is_gemini_configured
        self.api_url = settings.GEMINI_API_URL.format(model=self.model, api_key=self.api_key)
        
        if not self.is_configured:
            logger.warning("GEMINI_API_KEY не настроен или имеет неверный формат.")
    
    async def analyze_legal_query(self, query: str, documents: list) -> str:
        """Генерирует юридический анализ с помощью Gemini API"""
        if not self.is_configured:
            logger.info("Gemini API не настроен, используем резервный анализ")
            return self._create_fallback_analysis(query, documents)
            
        prompt = self._create_legal_prompt(query, documents)
        
        try:
            # ИСПРАВЛЕНО: правильные заголовки и формат запроса
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 8192,
                }
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                candidate = response_data.get("candidates", [{}])[0]
                content = candidate.get("content", {})
                parts = content.get("parts", [{}])
                
                if not parts or "text" not in parts[0]:
                    raise ValueError("Некорректный формат ответа от Gemini API")
                
                return parts[0]["text"]
                
        except Exception as e:
            logger.error(f"Ошибка вызова Gemini API: {str(e)}")
            if 'response' in locals():
                logger.error(f"Ответ сервера: {response.text}")
            return self._create_fallback_analysis(query, documents)
    
    # ДОБАВЛЕНО: метод резервного анализа
    def _create_fallback_analysis(self, query: str, documents: list) -> str:
        """Резервный анализ при ошибке Gemini API"""
        doc_count = len(documents)
        return f"""
## Анализ (РЕЗЕРВНЫЙ РЕЖИМ)

**Запрос юриста:**  
{query}

### Найдено материалов: {doc_count}

### Предварительные выводы:
Системе временно недоступен расширенный анализ из-за технических ограничений
Рекомендуется проанализировать найденные материалы вручную
Обратите особое внимание на судебную практику по аналогичным делам

### Что можно сделать:
1. Внимательно изучите найденные судебные решения
2. Сравните фактические обстоятельства вашего дела с рассмотренными в судебной практике
3. Обратитесь к специалисту для углубленного анализа

### Ключевые аспекты для самостоятельного анализа:
- Какие доказательства предоставили стороны в аналогичных делах?
- Какие нормы закона применили суды?
- Какие доводы оказались решающими для вынесения решения?

⚠️ **ВАЖНО**: Данный анализ является упрощенным и не заменяет консультацию квалифицированного юриста. Для принятия важных юридических решений обязательно обратитесь к специалисту.
"""

    def _create_legal_prompt(self, query: str, documents: list) -> str:
        """Создает детальный промпт для юридического анализа"""
        context = ""
        for i, doc in enumerate(documents[:8], 1):
            # Корректное извлечение данных из объектов Pydantic
            title = getattr(doc, 'title', 'Без названия')
            text = getattr(doc, 'text', getattr(doc, 'snippet', ''))
            source = getattr(doc, 'source', 'unknown')
            
            context += f"Документ #{i} (Источник: {source}):\n"
            context += f"Заголовок: {title}\n"
            context += f"Содержание: {text[:500]}...\n"
            context += f"{'-'*50}\n"
        
        return f"""
Вы - высококвалифицированный юрист с опытом работы в российских судах. Ваша задача - дать детальный юридический анализ ситуации, основанной на судебной практике.

ЗАПРОС ЮРИСТА:
"{query}"

КОНТЕКСТ (найденные материалы и судебная практика):
{context}

ИНСТРУКЦИЯ ДЛЯ АНАЛИЗА:
1. Проанализируйте найденные материалы по теме "{query}"
2. Выявите основные правовые позиции судов по аналогичным делам
3. Определите преобладающую судебную практику
4. Укажите применимые нормы российского законодательства
5. Оцените перспективы дела и юридические риски
6. Дайте практические рекомендации

ФОРМАТ ОТВЕТА (на русском языке, в формате Markdown):
## Краткое резюме ситуации

## Анализ судебной практики
- [Ключевые тенденции в решениях судов]
- [Статистика по удовлетворению/отказу в аналогичных исках]
- [Важные прецеденты]

## Применимое законодательство
- [Ключевые статьи ГК РФ, ГПК РФ, СК РФ и др.]
- [Разъяснения высших судебных инстанций]

## Правовые риски
- **Высокие риски**: [Описание наиболее вероятных негативных исходов]
- **Средние риски**: [Риски, требующие внимания]
- **Низкие риски**: [Маловероятные сценарии]

## Практические рекомендации
- [Конкретные шаги для клиента]
- [Какие доказательства необходимо собрать]
- [Тактика ведения дела в суде]

## Заключение
- [Общая оценка перспектив дела]
- [Рекомендуемая стратегия]

ДОПОЛНИТЕЛЬНЫЕ УКАЗАНИЯ:
- Будьте объективны и основывайтесь только на предоставленных данных
- Избегайте категоричных формулировок без достаточных оснований
- Обозначайте неопределенности и пробелы в информации
- Используйте юридическую терминологию корректно
- Если информации недостаточно для анализа какого-то аспекта, четко укажите это
"""