/**
 * 직업 카테고리 및 직업 목록 데이터
 */

export interface Job {
  name: string;
  icon: string;
}

export interface JobCategory {
  id: string;
  name: string;
  icon: string;
  jobs: Job[];
}

// 2024 교육부 진로교육 현황조사 기반 + 아이들 실제 인기 직업 반영
export const JOB_CATEGORIES: JobCategory[] = [
  {
    id: "sports",
    name: "운동선수",
    icon: "⚽",
    jobs: [
      { name: "축구선수", icon: "⚽" },
      { name: "야구선수", icon: "⚾" },
      { name: "농구선수", icon: "🏀" },
      { name: "수영선수", icon: "🏊" },
      { name: "태권도 선수", icon: "🥋" },
      { name: "체조선수", icon: "🤸" },
      { name: "피겨스케이팅 선수", icon: "⛸️" },
      { name: "배드민턴 선수", icon: "🏸" },
      { name: "e스포츠 선수", icon: "🎮" },
    ],
  },
  {
    id: "medical_science",
    name: "의료/과학",
    icon: "🔬",
    jobs: [
      { name: "의사", icon: "👨‍⚕️" },
      { name: "간호사", icon: "👩‍⚕️" },
      { name: "수의사", icon: "🐾" },
      { name: "과학자", icon: "🧪" },
      { name: "약사", icon: "💊" },
      { name: "치과의사", icon: "🦷" },
      { name: "한의사", icon: "🌿" },
      { name: "생물학자", icon: "🧬" },
    ],
  },
  {
    id: "creator_media",
    name: "크리에이터/미디어",
    icon: "📱",
    jobs: [
      { name: "유튜버", icon: "📺" },
      { name: "크리에이터", icon: "📱" },
      { name: "웹툰 작가", icon: "📝" },
      { name: "아나운서", icon: "🎙️" },
      { name: "기자", icon: "📰" },
      { name: "영화감독", icon: "🎬" },
      { name: "스트리머", icon: "🎥" },
    ],
  },
  {
    id: "arts_performance",
    name: "예술/공연",
    icon: "🎨",
    jobs: [
      { name: "가수", icon: "🎤" },
      { name: "배우", icon: "🎭" },
      { name: "화가", icon: "🖌️" },
      { name: "무용가", icon: "💃" },
      { name: "피아니스트", icon: "🎹" },
      { name: "바이올리니스트", icon: "🎻" },
      { name: "아이돌", icon: "⭐" },
      { name: "뮤지컬 배우", icon: "🎶" },
      { name: "패션 디자이너", icon: "👗" },
      { name: "사진작가", icon: "📷" },
    ],
  },
  {
    id: "food",
    name: "요리/제과",
    icon: "👨‍🍳",
    jobs: [
      { name: "요리사", icon: "👨‍🍳" },
      { name: "제빵사", icon: "🍞" },
      { name: "파티시에", icon: "🎂" },
      { name: "바리스타", icon: "☕" },
    ],
  },
  {
    id: "safety_law",
    name: "안전/법률",
    icon: "🚒",
    jobs: [
      { name: "경찰관", icon: "👮" },
      { name: "소방관", icon: "🧑‍🚒" },
      { name: "군인", icon: "🎖️" },
      { name: "판사", icon: "⚖️" },
      { name: "검사", icon: "📋" },
      { name: "변호사", icon: "👨‍⚖️" },
      { name: "구급대원", icon: "🚑" },
    ],
  },
  {
    id: "education",
    name: "교육",
    icon: "📚",
    jobs: [
      { name: "선생님", icon: "👩‍🏫" },
      { name: "유치원 선생님", icon: "🧒" },
      { name: "교수", icon: "🎓" },
      { name: "작가", icon: "✍️" },
    ],
  },
  {
    id: "tech_engineering",
    name: "기술/공학",
    icon: "💻",
    jobs: [
      { name: "프로그래머", icon: "👨‍💻" },
      { name: "게임 개발자", icon: "🎮" },
      { name: "로봇 공학자", icon: "🤖" },
      { name: "건축가", icon: "🏗️" },
      { name: "우주비행사", icon: "🚀" },
      { name: "발명가", icon: "💡" },
      { name: "AI 개발자", icon: "🧠" },
      { name: "자동차 엔지니어", icon: "🚗" },
    ],
  },
  {
    id: "nature_animals",
    name: "동물/자연",
    icon: "🌿",
    jobs: [
      { name: "동물 사육사", icon: "🦁" },
      { name: "해양생물학자", icon: "🐬" },
      { name: "농부", icon: "🌾" },
      { name: "꽃집 사장님", icon: "💐" },
      { name: "환경운동가", icon: "🌍" },
    ],
  },
  {
    id: "transport_adventure",
    name: "탐험/운송",
    icon: "✈️",
    jobs: [
      { name: "파일럿", icon: "✈️" },
      { name: "선장", icon: "🚢" },
      { name: "기차 기관사", icon: "🚂" },
      { name: "탐험가", icon: "🧭" },
      { name: "잠수부", icon: "🤿" },
    ],
  },
  {
    id: "business",
    name: "경영/사업",
    icon: "💼",
    jobs: [
      { name: "사업가", icon: "💼" },
      { name: "CEO", icon: "🏢" },
      { name: "은행원", icon: "🏦" },
      { name: "마케터", icon: "📊" },
    ],
  },
];

export const UNDECIDED_CATEGORY = {
  id: "undecided",
  name: "어떤 직업이 좋을지 모르겠어요",
  icon: "🤔",
};
