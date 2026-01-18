# backend/app/services/analyzer.py
import logging
from app.services.gemini import GeminiClient

logger = logging.getLogger(__name__)

class LegalAnalyzer:
    def __init__(self):
        self.gemini_client = GeminiClient()
        
    async def analyze(self, query: str, documents: list) -> str:
        """Генерирует юридический анализ с использованием Gemini API"""
        logger.info(f"Начало анализа запроса: '{query[:50]}...'")
        logger.info(f"Количество документов для анализа: {len(documents)}")
        
        for i, doc in enumerate(documents[:3]):
            logger.debug(f"Документ {i+1}: title={getattr(doc, 'title', 'неизвестно')}")
        
        try:
            analysis = await self.gemini_client.analyze_legal_query(query, documents)
            logger.info("Анализ успешно сгенерирован")
            return analysis
            
        except Exception as e:
            logger.error(f"Ошибка при генерации анализа: {str(e)}", exc_info=True)
            return self._error_analysis(str(e))
    
    def _error_analysis(self, error_message: str) -> str:
        """Анализ при ошибке"""
        return f"""
## Ошибка при юридическом анализе

**Техническая информация об ошибке:**  
{error_message}

### Рекомендуемые действия:

1. **Повторите запрос** - иногда ошибки носят временный характер
2. **Уточните формулировку запроса** - используйте более конкретные юридические термины
3. **Проверьте найденные материалы** - возможно, в них недостаточно информации для анализа
4. **Обратитесь к юристу** - для сложных вопросов необходима профессиональная консультация

### Что можно извлечь из найденных материалов:

- Прочитайте судебные решения по аналогичным делам
- Обратите внимание на правовые позиции судов
- Сравните вашу ситуацию с описанными в материалах случаями
- Выявите ключевые доказательства, которые суды считают значимыми

⚠️ **ВАЖНО**: Данный сервис является вспомогательным инструментом и не заменяет консультацию квалифицированного юриста. Для принятия важных юридических решений обязательно обратитесь к специалисту.
"""