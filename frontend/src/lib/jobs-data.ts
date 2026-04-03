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

export const JOB_CATEGORIES: JobCategory[] = [
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
    ],
  },
  {
    id: "arts_culture",
    name: "예술/문화",
    icon: "🎨",
    jobs: [
      { name: "화가", icon: "🖌️" },
      { name: "가수", icon: "🎤" },
      { name: "배우", icon: "🎭" },
      { name: "작가", icon: "✍️" },
      { name: "무용가", icon: "💃" },
    ],
  },
  {
    id: "safety_service",
    name: "안전/봉사",
    icon: "🚒",
    jobs: [
      { name: "소방관", icon: "🧑‍🚒" },
      { name: "경찰관", icon: "👮" },
      { name: "군인", icon: "🎖️" },
      { name: "해양경찰", icon: "⚓" },
    ],
  },
  {
    id: "tech_engineering",
    name: "기술/공학",
    icon: "💻",
    jobs: [
      { name: "프로그래머", icon: "👨‍💻" },
      { name: "로봇 공학자", icon: "🤖" },
      { name: "건축가", icon: "🏗️" },
      { name: "우주비행사", icon: "🚀" },
      { name: "자동차 엔지니어", icon: "🚗" },
    ],
  },
  {
    id: "education_sports",
    name: "교육/체육",
    icon: "📚",
    jobs: [
      { name: "선생님", icon: "👩‍🏫" },
      { name: "운동선수", icon: "⚽" },
      { name: "요리사", icon: "👨‍🍳" },
      { name: "피아니스트", icon: "🎹" },
      { name: "수영선수", icon: "🏊" },
    ],
  },
];

export const UNDECIDED_CATEGORY = {
  id: "undecided",
  name: "어떤 직업이 좋을지 모르겠어요",
  icon: "🤔",
};
