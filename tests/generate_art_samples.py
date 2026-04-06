"""그림체 샘플 이미지 5장 생성 스크립트

각 그림체별로 같은 장면("동화 속 작은 마을")을 다른 스타일로 생성한다.
결과물은 frontend/public/images/art-styles/ 에 저장.

사용법:
    cd backend
    python ../tests/generate_art_samples.py

필요: OPENAI_API_KEY 환경변수
"""
import os
import sys
import time
import base64

from openai import OpenAI

# .env 로드
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, BACKEND_DIR)

# .env 파일에서 키 읽기
env_path = os.path.join(BACKEND_DIR, ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not API_KEY:
    print("OPENAI_API_KEY 환경변수를 설정해주세요.")
    sys.exit(1)

# 출력 디렉토리
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend", "public", "images", "art-styles",
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 모델 설정
MODEL = "gpt-image-1-mini"
QUALITY = "medium"
SIZE = "1024x1024"

# 5가지 그림체 + 장면 프롬프트
STYLES = [
    {
        "id": "watercolor",
        "prompt": (
            "Watercolor illustration, soft wet-on-wet technique, translucent washes, gentle bleeding edges. "
            "A quiet forest path after rain, puddles on the ground reflecting a pastel sky, "
            "misty trees fading into the background, a few fallen autumn leaves floating on water, "
            "soft gray-blue and muted green tones. Peaceful and melancholic beauty. "
            "No people or characters. Children's storybook style. High quality."
        ),
    },
    {
        "id": "pastel",
        "prompt": (
            "Soft pastel illustration, dreamy chalky texture, muted purple and indigo tones. "
            "A magical sleeping forest under moonlight, tall silver birch trees with glowing fireflies, "
            "a crescent moon casting soft blue light, mushrooms with tiny glowing caps on the forest floor, "
            "everything bathed in a quiet ethereal purple-blue glow. "
            "No people or characters. Children's storybook style. High quality."
        ),
    },
    {
        "id": "crayon",
        "prompt": (
            "Crayon drawing, thick waxy strokes, bold primary colors, childlike imperfect charm. "
            "A happy farm with a big red barn, a rooster on the roof, spotted cows in a green field, "
            "yellow chicks, pink pigs rolling in mud, a bright yellow sun with triangle rays, "
            "a wooden fence drawn with wobbly lines. Cheerful and naive style. "
            "No people or characters. Children's storybook style. High quality."
        ),
    },
    {
        "id": "3d",
        "prompt": (
            "3D render, Pixar style, volumetric lighting, subsurface scattering, rounded smooth shapes. "
            "A vibrant underwater coral reef scene, colorful tropical fish swimming between coral formations, "
            "a friendly sea turtle gliding through, jellyfish with translucent glowing bodies, "
            "sunlight rays filtering through the turquoise water from above, bubbles rising. "
            "No people or characters. Children's storybook style. High quality."
        ),
    },
    {
        "id": "cartoon",
        "prompt": (
            "Cartoon style, cel-shaded, clean bold outlines, flat vibrant colors, dynamic composition. "
            "Outer space scene with a cute retro rocket ship blasting off with flame trail, "
            "colorful planets with rings and craters, twinkling stars, a smiling crescent moon, "
            "a spiral galaxy in the background, comets with glowing tails streaking across. "
            "No people or characters. Children's storybook style. High quality."
        ),
    },
]


def main():
    client = OpenAI(api_key=API_KEY, timeout=120.0)
    total_start = time.time()

    print(f"모델: {MODEL} / quality: {QUALITY} / size: {SIZE}")
    print(f"출력: {OUTPUT_DIR}")
    print(f"{'='*50}\n")

    for i, style in enumerate(STYLES):
        print(f"[{i+1}/5] {style['id']} 생성 중...")
        start = time.time()

        response = client.images.generate(
            model=MODEL,
            prompt=style["prompt"],
            size=SIZE,
            quality=QUALITY,
            output_format="png",
        )

        image_bytes = base64.b64decode(response.data[0].b64_json)
        filepath = os.path.join(OUTPUT_DIR, f"{style['id']}.png")
        with open(filepath, "wb") as f:
            f.write(image_bytes)

        elapsed = time.time() - start
        print(f"  완료! {elapsed:.1f}초 | {len(image_bytes)/1024:.0f}KB | {filepath}")

    total = time.time() - total_start
    cost = len(STYLES) * 0.011
    print(f"\n{'='*50}")
    print(f"전체 완료! {total:.1f}초 | 예상 비용: ~${cost:.3f} (약 {int(cost*1400)}원)")


if __name__ == "__main__":
    main()
