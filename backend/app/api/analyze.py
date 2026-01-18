from fastapi import APIRouter
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import LegalAnalyzer

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_cases(payload: AnalyzeRequest):
    analyzer = LegalAnalyzer()
    markdown = await analyzer.analyze(payload.query, payload.documents)
    return AnalyzeResponse(result=markdown)
