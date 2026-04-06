"""이미지 생성 품질 테스트 API (개발 전용)

인증 없이 samples/ 사진으로 캐릭터 + 일러스트를 테스트한다.
model/quality를 직접 지정하여 비교 테스트가 가능하다.
프로덕션에서는 반드시 제거할 것.
"""
import base64
import os
import uuid
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel

from app.config import get_settings
from app.services.ai_character import _build_character_prompt
from app.services.ai_illustration import _build_illustration_prompt
from app.services.photo import UPLOAD_DIR

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/test-image", tags=["test-image"])

# samples 디렉토리 (sweetbook/samples/)
SAMPLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
    "samples",
)
CHARACTER_DIR = os.path.join(UPLOAD_DIR, "characters")


class CharacterRequest(BaseModel):
    photo_file: str       # samples/ 폴더 내 파일명 (예: kid1.jpg)
    art_style: str
    job_name: str
    model: str = "gpt-image-1"       # gpt-image-1 / gpt-image-1-mini
    quality: str = "medium"           # low / medium / high


class CharacterResponse(BaseModel):
    image_path: str


class IllustrationRequest(BaseModel):
    character_sheet_path: str  # /uploads/characters/xxx.png
    scene_description: str
    art_style: str
    child_name: str
    job_name: str
    model: str = "gpt-image-1"
    quality: str = "medium"


class IllustrationResponse(BaseModel):
    image_path: str


def _get_client() -> OpenAI:
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        raise HTTPException(400, "OPENAI_API_KEY가 설정되지 않았습니다")
    return OpenAI(api_key=settings.OPENAI_API_KEY, timeout=120.0)


@router.get("/samples")
def list_samples():
    """samples/ 폴더의 사진 목록 반환"""
    if not os.path.isdir(SAMPLES_DIR):
        return {"files": []}
    files = [
        f for f in os.listdir(SAMPLES_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]
    return {"files": sorted(files)}


@router.get("/samples/{filename}")
def get_sample_photo(filename: str):
    """samples/ 폴더의 사진 파일 서빙"""
    filepath = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(404, "파일 없음")
    return FileResponse(filepath)


@router.post("/character", response_model=CharacterResponse)
def generate_test_character(req: CharacterRequest):
    """samples/ 사진으로 캐릭터 시트 생성 (model/quality 지정 가능)"""
    client = _get_client()

    photo_path = os.path.join(SAMPLES_DIR, req.photo_file)
    if not os.path.exists(photo_path):
        raise HTTPException(404, f"사진 파일 없음: {req.photo_file}")

    prompt = _build_character_prompt(req.art_style, req.job_name)

    photo_file = open(photo_path, "rb")
    try:
        response = client.images.edit(
            model=req.model,
            image=photo_file,
            prompt=prompt,
            size="1024x1024",
            quality=req.quality,
            output_format="png",
        )
    finally:
        photo_file.close()

    image_bytes = base64.b64decode(response.data[0].b64_json)

    os.makedirs(CHARACTER_DIR, exist_ok=True)
    tag = f"{req.model}_{req.quality}"
    filename = f"test_char_{tag}_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(CHARACTER_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return CharacterResponse(image_path=f"/uploads/characters/{filename}")


@router.post("/illustration", response_model=IllustrationResponse)
def generate_test_illustration(req: IllustrationRequest):
    """캐릭터 시트 기반 일러스트 생성 (model/quality 지정 가능)"""
    client = _get_client()

    # /uploads/characters/xxx.png → 실제 파일 경로로 변환
    char_path = os.path.join(
        UPLOAD_DIR, "characters",
        os.path.basename(req.character_sheet_path),
    )
    if not os.path.exists(char_path):
        # lstrip 방식도 시도
        char_path = os.path.join(UPLOAD_DIR, req.character_sheet_path.lstrip("/uploads/"))
    if not os.path.exists(char_path):
        raise HTTPException(404, f"캐릭터 시트 없음: {req.character_sheet_path}")

    prompt = _build_illustration_prompt(
        req.art_style, req.scene_description, req.child_name, req.job_name,
    )

    photo_file = open(char_path, "rb")
    try:
        response = client.images.edit(
            model=req.model,
            image=photo_file,
            prompt=prompt,
            size="1024x1024",
            quality=req.quality,
            output_format="png",
        )
    finally:
        photo_file.close()

    image_bytes = base64.b64decode(response.data[0].b64_json)

    tag = f"{req.model}_{req.quality}"
    filename = f"test_illust_{tag}_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return IllustrationResponse(image_path=f"/uploads/{filename}")
