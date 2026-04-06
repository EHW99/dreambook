"""이미지 생성 품질 테스트 스크립트

samples/ 폴더의 아이 사진 → 캐릭터 시트 생성 → 일러스트 3장 생성
실제 파이프라인(ai_character.py, ai_illustration.py)을 그대로 사용한다.

사용법:
    cd backend
    python -m tests.test_image_quality

필요:
    OPENAI_API_KEY 환경변수 설정
"""
import os
import sys
import time
import base64
import logging

# backend 디렉토리를 path에 추가
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "backend")
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))

from app.services.ai_character import generate_character_image
from app.services.ai_illustration import generate_illustration_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────
SAMPLES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "samples")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "image_quality_output")
PHOTO_FILE = "kid1.jpg"  # samples/ 폴더에서 사용할 사진

CHILD_NAME = "하준"
JOB_NAME = "소방관"
ART_STYLE = "watercolor"

# 테스트용 스토리 3장 (도입 / 절정 / 결말)
TEST_SCENES = [
    {
        "story_number": 1,
        "text": "오늘도 소방관 하준이의 하루가 시작되었어요. 빨간 소방복의 단추를 하나하나 채우고, 반짝이는 헬멧을 쓰자 기분이 정말 좋았어요. '좋아, 오늘도 마을을 지키러 출발이다!'",
        "scene_description": (
            "A confident child firefighter (age 6) in a bright red uniform buttoning up "
            "their coat, standing in front of a gleaming red fire truck at the fire station "
            "entrance. The child has a determined and cheerful expression, morning sunlight "
            "casting a warm glow. Background: the fire station with large open bay doors, "
            "a clear blue sky. Composition: character on the left, fire truck behind, "
            "warm morning light, space at top for text."
        ),
    },
    {
        "story_number": 2,
        "text": "삐뽀삐뽀! 빵집에서 큰불이 났어요! 하준이는 소방차에서 뛰어내려 무거운 호스를 꽉 잡았어요. 뜨거운 연기가 자욱했지만, 안에 할머니가 갇혀 계신다는 말에 하준이는 물러서지 않았어요.",
        "scene_description": (
            "A brave child firefighter (age 6) charging into a smoke-filled bakery doorway, "
            "gripping a fire hose with both hands and spraying a powerful stream of water. "
            "Flames flicker from the windows above, thick gray smoke billows into the sky. "
            "Fellow firefighters in the background operate the fire truck. The child's "
            "expression is fierce and determined, helmet reflecting the orange glow of fire. "
            "Background: small-town street, fire truck with flashing red lights. "
            "Composition: dynamic action shot, dramatic lighting from flames, space at top for text."
        ),
    },
    {
        "story_number": 3,
        "text": "할머니를 무사히 구해낸 하준이는 소방서 앞에서 동료들과 함께 환하게 웃었어요. 마을 사람들이 '고마워요, 하준이!' 하고 손을 흔들었어요. 하준이는 헬멧을 꼭 안으며 속삭였어요. '내일도 이 마을을 지킬 거야.'",
        "scene_description": (
            "A child firefighter (age 6) standing proudly in front of the fire station, "
            "surrounded by cheering townspeople and fellow firefighters. An elderly grandmother "
            "wrapped in a blanket smiles and waves gratefully. The child hugs their helmet "
            "with a warm, content smile. Background: golden hour light, the fire station "
            "with its red doors, bunting and flowers. Composition: child in center, crowd "
            "around them, warm golden light, space at bottom for text."
        ),
    },
]


def main():
    # API 키 확인
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("OPENAI_API_KEY 환경변수를 설정해주세요.")
        print("  set OPENAI_API_KEY=sk-...")
        sys.exit(1)

    # 사진 파일 확인
    photo_path = os.path.join(SAMPLES_DIR, PHOTO_FILE)
    if not os.path.exists(photo_path):
        print(f"사진 파일 없음: {photo_path}")
        print(f"samples/ 폴더 파일: {os.listdir(SAMPLES_DIR)}")
        sys.exit(1)

    # 출력 디렉토리 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total_start = time.time()

    # ── Step 1: 캐릭터 시트 생성 ──
    print(f"\n{'='*50}")
    print(f"Step 1: 캐릭터 시트 생성")
    print(f"  사진: {PHOTO_FILE}")
    print(f"  그림체: {ART_STYLE}")
    print(f"  직업: {JOB_NAME}")
    print(f"{'='*50}")

    start = time.time()
    character_bytes = generate_character_image(
        photo_path=photo_path,
        art_style=ART_STYLE,
        job_name=JOB_NAME,
    )
    elapsed = time.time() - start

    character_path = os.path.join(OUTPUT_DIR, "character_sheet.png")
    with open(character_path, "wb") as f:
        f.write(character_bytes)

    print(f"  완료! {elapsed:.1f}초 | {len(character_bytes)/1024:.0f}KB")
    print(f"  저장: {character_path}")

    # ── Step 2: 일러스트 3장 순차 생성 ──
    print(f"\n{'='*50}")
    print(f"Step 2: 일러스트 3장 생성 (순차)")
    print(f"{'='*50}")

    for i, scene in enumerate(TEST_SCENES):
        print(f"\n  [{i+1}/3] 이야기 {scene['story_number']}")
        print(f"  내용: {scene['text'][:40]}...")

        start = time.time()
        illust_bytes = generate_illustration_image(
            character_sheet_path=character_path,
            scene_description=scene["scene_description"],
            art_style=ART_STYLE,
            child_name=CHILD_NAME,
            job_name=JOB_NAME,
        )
        elapsed = time.time() - start

        illust_path = os.path.join(OUTPUT_DIR, f"page_{scene['story_number']}.png")
        with open(illust_path, "wb") as f:
            f.write(illust_bytes)

        print(f"  완료! {elapsed:.1f}초 | {len(illust_bytes)/1024:.0f}KB")
        print(f"  저장: {illust_path}")

    # ── 결과 요약 ──
    total_elapsed = time.time() - total_start
    print(f"\n{'='*50}")
    print(f"완료! 총 {total_elapsed:.1f}초")
    print(f"{'='*50}")
    print(f"출력 폴더: {OUTPUT_DIR}")
    print(f"  - character_sheet.png  (캐릭터 시트)")
    print(f"  - page_1.png           (도입)")
    print(f"  - page_2.png           (절정)")
    print(f"  - page_3.png           (결말)")
    print(f"\n예상 비용: 이미지 4장 × $0.02 = ~$0.08 (약 110원)")


if __name__ == "__main__":
    main()
