"""성향 테스트 API 라우터"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List

from app.services.aptitude_test import get_aptitude_questions, calculate_aptitude_result

router = APIRouter(prefix="/api/aptitude")


class AptitudeAnswerRequest(BaseModel):
    """성향 테스트 답변 요청"""
    answers: Dict[int, str]  # {질문ID: 선택옵션ID}


class JobRecommendation(BaseModel):
    name: str
    icon: str
    desc: str


class AptitudeResultResponse(BaseModel):
    category_id: str
    category_name: str
    recommended_jobs: List[JobRecommendation]
    scores: Dict[str, int]


@router.get("/questions")
def questions():
    """성향 테스트 질문 목록 조회 (비로그인 가능)"""
    return get_aptitude_questions()


@router.post("/result", response_model=AptitudeResultResponse)
def result(req: AptitudeAnswerRequest):
    """성향 테스트 결과 계산 (비로그인 가능)"""
    return calculate_aptitude_result(req.answers)
