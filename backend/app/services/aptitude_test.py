"""성향 테스트 서비스 — 규칙 기반 직업 추천

AI 호출 없이 간단한 규칙으로 직업을 추천한다.
3~5개 질문에 답하면 점수 기반으로 직업 카테고리를 추천.
"""
from typing import List, Optional


# ──────────────────────────────────────────────
# 질문 데이터
# ──────────────────────────────────────────────
QUESTIONS = [
    {
        "id": 1,
        "text": "친구가 다쳤을 때 어떻게 할까요?",
        "options": [
            {"id": "a", "text": "빨리 달려가서 도와줘요", "scores": {"safety_service": 3, "medical_science": 2}},
            {"id": "b", "text": "어른을 불러올게요", "scores": {"education_sports": 2, "safety_service": 1}},
            {"id": "c", "text": "반창고를 가져와요", "scores": {"medical_science": 3, "safety_service": 1}},
            {"id": "d", "text": "친구를 웃겨서 기분 좋게 해줘요", "scores": {"arts_culture": 3, "education_sports": 1}},
        ],
    },
    {
        "id": 2,
        "text": "가장 좋아하는 놀이는 뭔가요?",
        "options": [
            {"id": "a", "text": "블록이나 레고 만들기", "scores": {"tech_engineering": 3, "arts_culture": 1}},
            {"id": "b", "text": "그림 그리기나 색칠하기", "scores": {"arts_culture": 3, "education_sports": 1}},
            {"id": "c", "text": "달리기나 공놀이", "scores": {"education_sports": 3, "safety_service": 1}},
            {"id": "d", "text": "동물이나 식물 돌보기", "scores": {"medical_science": 3, "education_sports": 1}},
        ],
    },
    {
        "id": 3,
        "text": "마법의 힘이 생긴다면 뭘 하고 싶어요?",
        "options": [
            {"id": "a", "text": "아픈 사람을 낫게 해줘요", "scores": {"medical_science": 3, "safety_service": 1}},
            {"id": "b", "text": "로봇 친구를 만들어요", "scores": {"tech_engineering": 3, "medical_science": 1}},
            {"id": "c", "text": "멋진 노래를 불러요", "scores": {"arts_culture": 3, "education_sports": 1}},
            {"id": "d", "text": "불을 끄고 사람들을 구해요", "scores": {"safety_service": 3, "tech_engineering": 1}},
        ],
    },
    {
        "id": 4,
        "text": "학교에서 가장 재미있는 시간은?",
        "options": [
            {"id": "a", "text": "과학 실험 시간", "scores": {"medical_science": 2, "tech_engineering": 2}},
            {"id": "b", "text": "미술이나 음악 시간", "scores": {"arts_culture": 3, "education_sports": 1}},
            {"id": "c", "text": "체육 시간", "scores": {"education_sports": 3, "safety_service": 1}},
            {"id": "d", "text": "컴퓨터 시간", "scores": {"tech_engineering": 3, "arts_culture": 1}},
        ],
    },
    {
        "id": 5,
        "text": "커서 어떤 사람이 되고 싶어요?",
        "options": [
            {"id": "a", "text": "사람들을 지켜주는 사람", "scores": {"safety_service": 3, "medical_science": 1}},
            {"id": "b", "text": "새로운 것을 만드는 사람", "scores": {"tech_engineering": 3, "arts_culture": 1}},
            {"id": "c", "text": "아이들을 가르치는 사람", "scores": {"education_sports": 3, "medical_science": 1}},
            {"id": "d", "text": "무대에서 빛나는 사람", "scores": {"arts_culture": 3, "education_sports": 1}},
        ],
    },
]

# 카테고리별 추천 직업 (상위 2개)
CATEGORY_JOBS = {
    "medical_science": [
        {"name": "의사", "icon": "👨‍⚕️", "desc": "아픈 사람들을 치료해요"},
        {"name": "과학자", "icon": "🧪", "desc": "신기한 것들을 발견해요"},
    ],
    "arts_culture": [
        {"name": "화가", "icon": "🖌️", "desc": "아름다운 그림을 그려요"},
        {"name": "가수", "icon": "🎤", "desc": "멋진 노래를 불러요"},
    ],
    "safety_service": [
        {"name": "소방관", "icon": "🧑‍🚒", "desc": "불을 끄고 사람들을 구해요"},
        {"name": "경찰관", "icon": "👮", "desc": "사람들을 지켜줘요"},
    ],
    "tech_engineering": [
        {"name": "프로그래머", "icon": "👨‍💻", "desc": "컴퓨터로 멋진 것을 만들어요"},
        {"name": "로봇 공학자", "icon": "🤖", "desc": "로봇을 만들어요"},
    ],
    "education_sports": [
        {"name": "선생님", "icon": "👩‍🏫", "desc": "아이들을 가르쳐요"},
        {"name": "운동선수", "icon": "⚽", "desc": "멋지게 운동해요"},
    ],
}

CATEGORY_NAMES = {
    "medical_science": "의료/과학",
    "arts_culture": "예술/문화",
    "safety_service": "안전/봉사",
    "tech_engineering": "기술/공학",
    "education_sports": "교육/체육",
}


def get_aptitude_questions() -> list:
    """성향 테스트 질문 목록을 반환한다."""
    return QUESTIONS


def calculate_aptitude_result(answers: dict[int, str]) -> dict:
    """답변을 기반으로 직업 추천 결과를 계산한다.

    Args:
        answers: {질문ID: 선택한 옵션ID} — 예: {1: "a", 2: "b", 3: "c", 4: "d", 5: "a"}

    Returns:
        {
            "category_id": "medical_science",
            "category_name": "의료/과학",
            "recommended_jobs": [...],
            "scores": {"medical_science": 10, ...},
        }
    """
    scores: dict[str, int] = {
        "medical_science": 0,
        "arts_culture": 0,
        "safety_service": 0,
        "tech_engineering": 0,
        "education_sports": 0,
    }

    for q in QUESTIONS:
        answer = answers.get(q["id"])
        if not answer:
            continue
        for option in q["options"]:
            if option["id"] == answer:
                for category, score in option["scores"].items():
                    scores[category] = scores.get(category, 0) + score
                break

    # 최고 점수 카테고리
    top_category = max(scores, key=lambda k: scores[k])

    return {
        "category_id": top_category,
        "category_name": CATEGORY_NAMES[top_category],
        "recommended_jobs": CATEGORY_JOBS[top_category],
        "scores": scores,
    }
