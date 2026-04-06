"""성향 테스트 서비스 — 규칙 기반 직업 추천

AI 호출 없이 규칙 기반으로 직업을 추천한다.
7개 질문에 답하면 점수 기반으로 직업 카테고리를 추천.
2024 교육부 진로교육 현황조사 기반 11개 카테고리.
"""
from typing import List, Optional


# ──────────────────────────────────────────────
# 질문 데이터 (7문항)
# ──────────────────────────────────────────────
QUESTIONS = [
    {
        "id": 1,
        "text": "쉬는 시간에 가장 하고 싶은 건?",
        "options": [
            {"id": "a", "text": "밖에 나가서 뛰어놀기", "scores": {"sports": 3, "transport_adventure": 1}},
            {"id": "b", "text": "그림 그리거나 노래 부르기", "scores": {"arts_performance": 3, "creator_media": 1}},
            {"id": "c", "text": "책 읽거나 실험하기", "scores": {"medical_science": 2, "education": 2}},
            {"id": "d", "text": "친구들이랑 역할놀이", "scores": {"safety_law": 2, "education": 1, "arts_performance": 1}},
        ],
    },
    {
        "id": 2,
        "text": "동물원에 갔을 때 가장 먼저 하고 싶은 건?",
        "options": [
            {"id": "a", "text": "동물들을 직접 만져보고 싶어요", "scores": {"nature_animals": 3, "medical_science": 1}},
            {"id": "b", "text": "동물 사진이나 영상을 찍고 싶어요", "scores": {"creator_media": 3, "arts_performance": 1}},
            {"id": "c", "text": "동물이 어떻게 사는지 알고 싶어요", "scores": {"medical_science": 2, "nature_animals": 2}},
            {"id": "d", "text": "동물을 위한 집을 만들어주고 싶어요", "scores": {"tech_engineering": 2, "nature_animals": 2}},
        ],
    },
    {
        "id": 3,
        "text": "마법의 힘이 생긴다면?",
        "options": [
            {"id": "a", "text": "아픈 사람을 낫게 해줄래요", "scores": {"medical_science": 3, "safety_law": 1}},
            {"id": "b", "text": "맛있는 음식을 뚝딱 만들 거예요", "scores": {"food": 3, "business": 1}},
            {"id": "c", "text": "하늘을 날아다니며 세계 여행!", "scores": {"transport_adventure": 3, "sports": 1}},
            {"id": "d", "text": "나쁜 사람을 물리칠 거예요", "scores": {"safety_law": 3, "sports": 1}},
        ],
    },
    {
        "id": 4,
        "text": "학교에서 가장 재미있는 시간은?",
        "options": [
            {"id": "a", "text": "체육 시간", "scores": {"sports": 3, "safety_law": 1}},
            {"id": "b", "text": "미술이나 음악 시간", "scores": {"arts_performance": 3, "creator_media": 1}},
            {"id": "c", "text": "과학이나 수학 시간", "scores": {"medical_science": 2, "tech_engineering": 2}},
            {"id": "d", "text": "컴퓨터나 코딩 시간", "scores": {"tech_engineering": 3, "creator_media": 1}},
        ],
    },
    {
        "id": 5,
        "text": "친구 생일에 해주고 싶은 건?",
        "options": [
            {"id": "a", "text": "직접 케이크를 만들어줄래요", "scores": {"food": 3, "arts_performance": 1}},
            {"id": "b", "text": "재밌는 영상을 만들어서 보여줄래요", "scores": {"creator_media": 3, "tech_engineering": 1}},
            {"id": "c", "text": "깜짝 파티를 계획할 거예요", "scores": {"business": 2, "education": 2}},
            {"id": "d", "text": "멋진 노래나 춤을 보여줄래요", "scores": {"arts_performance": 3, "sports": 1}},
        ],
    },
    {
        "id": 6,
        "text": "TV에서 가장 좋아하는 프로그램은?",
        "options": [
            {"id": "a", "text": "스포츠 경기 중계", "scores": {"sports": 3}},
            {"id": "b", "text": "요리 프로그램", "scores": {"food": 3}},
            {"id": "c", "text": "동물이나 자연 다큐", "scores": {"nature_animals": 3}},
            {"id": "d", "text": "과학이나 우주 다큐", "scores": {"tech_engineering": 2, "transport_adventure": 2}},
        ],
    },
    {
        "id": 7,
        "text": "커서 어떤 사람이 되고 싶어요?",
        "options": [
            {"id": "a", "text": "사람들을 지켜주는 사람", "scores": {"safety_law": 3, "medical_science": 1}},
            {"id": "b", "text": "많은 사람 앞에서 빛나는 사람", "scores": {"arts_performance": 2, "creator_media": 2}},
            {"id": "c", "text": "새로운 걸 발견하거나 만드는 사람", "scores": {"tech_engineering": 2, "medical_science": 1, "transport_adventure": 1}},
            {"id": "d", "text": "아이들을 가르치는 사람", "scores": {"education": 3, "medical_science": 1}},
        ],
    },
]

# 카테고리별 추천 직업 (상위 3개)
CATEGORY_JOBS = {
    "sports": [
        {"name": "축구선수", "icon": "⚽", "desc": "필드에서 골을 넣어요"},
        {"name": "수영선수", "icon": "🏊", "desc": "물속에서 가장 빠르게 헤엄쳐요"},
        {"name": "태권도 선수", "icon": "🥋", "desc": "멋진 발차기로 메달을 따요"},
    ],
    "medical_science": [
        {"name": "의사", "icon": "👨‍⚕️", "desc": "아픈 사람들을 치료해요"},
        {"name": "수의사", "icon": "🐾", "desc": "아픈 동물을 돌봐줘요"},
        {"name": "과학자", "icon": "🧪", "desc": "신기한 것들을 발견해요"},
    ],
    "creator_media": [
        {"name": "유튜버", "icon": "📺", "desc": "재밌는 영상을 만들어요"},
        {"name": "크리에이터", "icon": "📱", "desc": "멋진 콘텐츠를 만들어요"},
        {"name": "웹툰 작가", "icon": "📝", "desc": "재밌는 만화를 그려요"},
    ],
    "arts_performance": [
        {"name": "가수", "icon": "🎤", "desc": "멋진 노래를 불러요"},
        {"name": "배우", "icon": "🎭", "desc": "다양한 역할을 연기해요"},
        {"name": "화가", "icon": "🖌️", "desc": "아름다운 그림을 그려요"},
    ],
    "food": [
        {"name": "요리사", "icon": "👨‍🍳", "desc": "맛있는 요리를 만들어요"},
        {"name": "파티시에", "icon": "🎂", "desc": "예쁜 디저트를 만들어요"},
        {"name": "제빵사", "icon": "🍞", "desc": "맛있는 빵을 구워요"},
    ],
    "safety_law": [
        {"name": "경찰관", "icon": "👮", "desc": "사람들을 지켜줘요"},
        {"name": "소방관", "icon": "🧑‍🚒", "desc": "불을 끄고 사람들을 구해요"},
        {"name": "군인", "icon": "🎖️", "desc": "나라를 지켜요"},
    ],
    "education": [
        {"name": "선생님", "icon": "👩‍🏫", "desc": "아이들을 가르쳐요"},
        {"name": "유치원 선생님", "icon": "🧒", "desc": "어린 친구들을 돌봐요"},
        {"name": "작가", "icon": "✍️", "desc": "멋진 이야기를 써요"},
    ],
    "tech_engineering": [
        {"name": "프로그래머", "icon": "👨‍💻", "desc": "컴퓨터로 멋진 것을 만들어요"},
        {"name": "게임 개발자", "icon": "🎮", "desc": "재밌는 게임을 만들어요"},
        {"name": "로봇 공학자", "icon": "🤖", "desc": "로봇을 만들어요"},
    ],
    "nature_animals": [
        {"name": "동물 사육사", "icon": "🦁", "desc": "동물들을 돌봐요"},
        {"name": "해양생물학자", "icon": "🐬", "desc": "바다 생물을 연구해요"},
        {"name": "수의사", "icon": "🐾", "desc": "아픈 동물을 치료해요"},
    ],
    "transport_adventure": [
        {"name": "파일럿", "icon": "✈️", "desc": "하늘을 날아요"},
        {"name": "탐험가", "icon": "🧭", "desc": "세계를 탐험해요"},
        {"name": "우주비행사", "icon": "🚀", "desc": "우주로 날아가요"},
    ],
    "business": [
        {"name": "사업가", "icon": "💼", "desc": "멋진 회사를 만들어요"},
        {"name": "CEO", "icon": "🏢", "desc": "회사를 이끌어요"},
        {"name": "마케터", "icon": "📊", "desc": "좋은 아이디어를 알려요"},
    ],
}

CATEGORY_NAMES = {
    "sports": "운동선수",
    "medical_science": "의료/과학",
    "creator_media": "크리에이터/미디어",
    "arts_performance": "예술/공연",
    "food": "요리/제과",
    "safety_law": "안전/법률",
    "education": "교육",
    "tech_engineering": "기술/공학",
    "nature_animals": "동물/자연",
    "transport_adventure": "탐험/운송",
    "business": "경영/사업",
}


def get_aptitude_questions() -> list:
    """성향 테스트 질문 목록을 반환한다."""
    return QUESTIONS


def calculate_aptitude_result(answers: dict[int, str]) -> dict:
    """답변을 기반으로 직업 추천 결과를 계산한다.

    Args:
        answers: {질문ID: 선택한 옵션ID} — 예: {1: "a", 2: "b", ...}

    Returns:
        {
            "category_id": "sports",
            "category_name": "운동선수",
            "recommended_jobs": [...],
            "scores": {"sports": 10, ...},
        }
    """
    scores: dict[str, int] = {cat_id: 0 for cat_id in CATEGORY_NAMES}

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
