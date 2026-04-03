from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "ok", "service": "dreambook-api"}
