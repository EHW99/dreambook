"use client";

import { useState, useEffect } from "react";
import {
  Droplets, Palette, Box, Zap,
  Check, Loader2, ImageIcon,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const ART_STYLES = [
  { id: "watercolor", title: "���채화", icon: Droplets, color: "#A8DADC" },
  { id: "pastel", title: "파스텔", icon: Droplets, color: "#D4A5D6" },
  { id: "crayon", title: "크레파스", icon: Palette, color: "#FFB5A7" },
  { id: "3d", title: "3D", icon: Box, color: "#7C9EF7" },
  { id: "cartoon", title: "만화", icon: Zap, color: "#FFE0AC" },
];

const TEST_SCENES = [
  {
    label: "도입",
    scene_description:
      "A confident child firefighter (age 6) in a bright red uniform buttoning up their coat, standing in front of a gleaming red fire truck at the fire station entrance. The child has a determined and cheerful expression, morning sunlight casting a warm glow. Background: the fire station with large open bay doors, a clear blue sky. Composition: character on the left, fire truck behind, warm morning light, space at top for text.",
  },
  {
    label: "절정",
    scene_description:
      "A brave child firefighter (age 6) charging into a smoke-filled bakery doorway, gripping a fire hose with both hands and spraying a powerful stream of water. Flames flicker from the windows above, thick gray smoke billows into the sky. Fellow firefighters in the background operate the fire truck. The child's expression is fierce and determined, helmet reflecting the orange glow of fire. Background: small-town street, fire truck with flashing red lights. Composition: dynamic action shot, dramatic lighting from flames, space at top for text.",
  },
  {
    label: "결말",
    scene_description:
      "A child firefighter (age 6) standing proudly in front of the fire station, surrounded by cheering townspeople and fellow firefighters. An elderly grandmother wrapped in a blanket smiles and waves gratefully. The child hugs their helmet with a warm, content smile. Background: golden hour light, the fire station with its red doors, bunting and flowers. Composition: child in center, crowd around them, warm golden light, space at bottom for text.",
  },
];

// 비교할 두 모델 설정
const MODEL_CONFIGS = [
  { id: "A", model: "gpt-image-1-mini", quality: "medium", label: "mini / medium", costPerImage: 0.011 },
  { id: "B", model: "gpt-image-1", quality: "low", label: "standard / low", costPerImage: 0.011 },
];

interface StepStatus {
  state: "idle" | "loading" | "done" | "error";
  elapsed?: number;
  error?: string;
}

function SamplePhoto({
  file, isSelected, onClick,
}: {
  file: string; isSelected: boolean; onClick: () => void;
}) {
  const [imgOk, setImgOk] = useState(true);
  return (
    <button
      onClick={onClick}
      className={`relative rounded-xl overflow-hidden border-2 transition-all aspect-square bg-gray-100 ${
        isSelected ? "border-blue-500 ring-2 ring-blue-200" : "border-gray-200 hover:border-gray-300"
      }`}
    >
      {imgOk ? (
        <img
          src={`${API_BASE}/api/test-image/samples/${file}`}
          alt={file}
          className="w-full h-full object-cover"
          onError={() => setImgOk(false)}
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center">
          <span className="text-xs text-gray-500">{file}</span>
        </div>
      )}
      {isSelected && (
        <div className="absolute top-1 right-1 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center z-10">
          <Check className="w-3 h-3 text-white" />
        </div>
      )}
    </button>
  );
}

// 한 줄(한 모델) 테스트 결과 컴포넌트
function ModelRow({
  config,
  selectedPhoto,
  selectedStyle,
  childName,
  jobName,
  disabled,
}: {
  config: typeof MODEL_CONFIGS[0];
  selectedPhoto: string;
  selectedStyle: string;
  childName: string;
  jobName: string;
  disabled: boolean;
}) {
  const [characterPath, setCharacterPath] = useState("");
  const [illustPaths, setIllustPaths] = useState<string[]>([]);
  const [charStatus, setCharStatus] = useState<StepStatus>({ state: "idle" });
  const [illustStatuses, setIllustStatuses] = useState<StepStatus[]>(
    TEST_SCENES.map(() => ({ state: "idle" }))
  );

  const isLoading = charStatus.state === "loading" || illustStatuses.some((s) => s.state === "loading");
  const imageCount = (charStatus.state === "done" ? 1 : 0) + illustPaths.length;
  const cost = imageCount * config.costPerImage;

  async function handleGenerate() {
    if (!selectedPhoto || !selectedStyle) return;

    // reset
    setCharacterPath("");
    setIllustPaths([]);
    setIllustStatuses(TEST_SCENES.map(() => ({ state: "idle" })));

    // ── 캐릭터 생성 ──
    setCharStatus({ state: "loading" });
    let charPath = "";
    const charStart = Date.now();
    try {
      const res = await fetch(`${API_BASE}/api/test-image/character`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          photo_file: selectedPhoto,
          art_style: selectedStyle,
          job_name: jobName,
          model: config.model,
          quality: config.quality,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "캐릭터 생성 실패");
      }
      const data = await res.json();
      charPath = data.image_path;
      setCharacterPath(charPath);
      setCharStatus({ state: "done", elapsed: (Date.now() - charStart) / 1000 });
    } catch (e: any) {
      setCharStatus({ state: "error", error: e.message, elapsed: (Date.now() - charStart) / 1000 });
      return;
    }

    // ── 일러스트 3장 순차 생성 ──
    const paths: string[] = [];
    for (let i = 0; i < TEST_SCENES.length; i++) {
      setIllustStatuses((prev) =>
        prev.map((s, idx) => (idx === i ? { state: "loading" } : s))
      );
      const start = Date.now();
      try {
        const res = await fetch(`${API_BASE}/api/test-image/illustration`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            character_sheet_path: charPath,
            scene_description: TEST_SCENES[i].scene_description,
            art_style: selectedStyle,
            child_name: childName,
            job_name: jobName,
            model: config.model,
            quality: config.quality,
          }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(err.detail || "일러스트 생성 실패");
        }
        const data = await res.json();
        paths.push(data.image_path);
        setIllustPaths([...paths]);
        setIllustStatuses((prev) =>
          prev.map((s, idx) =>
            idx === i ? { state: "done", elapsed: (Date.now() - start) / 1000 } : s
          )
        );
      } catch (e: any) {
        setIllustStatuses((prev) =>
          prev.map((s, idx) =>
            idx === i ? { state: "error", error: e.message, elapsed: (Date.now() - start) / 1000 } : s
          )
        );
        break;
      }
    }
  }

  const totalElapsed = [
    charStatus.elapsed || 0,
    ...illustStatuses.map((s) => s.elapsed || 0),
  ].reduce((a, b) => a + b, 0);

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold">
            <span className="inline-block px-2 py-0.5 rounded bg-gray-800 text-white text-xs mr-2">
              {config.id}
            </span>
            {config.model}
            <span className="text-gray-400 font-normal ml-1">/ {config.quality}</span>
          </h3>
          <p className="text-xs text-gray-400 mt-1">
            ~${config.costPerImage}/장
            {cost > 0 && (
              <span className="text-orange-500 ml-2">
                현재: ${cost.toFixed(3)} ({totalElapsed.toFixed(1)}초)
              </span>
            )}
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={!selectedPhoto || !selectedStyle || isLoading || disabled}
          className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium disabled:opacity-40 hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              생성 중...
            </>
          ) : (
            <>
              <ImageIcon className="w-4 h-4" />
              캐���터 + 일러스트 3장 생성
            </>
          )}
        </button>
      </div>

      {/* 결과 이미지 4장 */}
      <div className="grid grid-cols-4 gap-3">
        {/* 캐릭터 */}
        <div className="space-y-1">
          <div className="aspect-square rounded-xl border-2 border-dashed border-gray-200 overflow-hidden bg-gray-50 flex items-center justify-center">
            {characterPath ? (
              <img src={`${API_BASE}${characterPath}`} alt="캐릭터" className="w-full h-full object-cover" />
            ) : charStatus.state === "loading" ? (
              <div className="text-center">
                <Loader2 className="w-6 h-6 animate-spin text-gray-300 mx-auto" />
                <span className="text-[10px] text-gray-400 mt-1 block">캐릭터...</span>
              </div>
            ) : (
              <span className="text-gray-300 text-[10px]">캐릭터</span>
            )}
          </div>
          <p className="text-[11px] text-center font-medium">캐릭터</p>
          {charStatus.state === "done" && (
            <p className="text-[10px] text-center text-green-600">{charStatus.elapsed?.toFixed(1)}초</p>
          )}
          {charStatus.state === "error" && (
            <p className="text-[10px] text-center text-red-500 truncate" title={charStatus.error}>{charStatus.error}</p>
          )}
        </div>

        {/* 일러스트 3장 */}
        {TEST_SCENES.map((scene, i) => (
          <div key={i} className="space-y-1">
            <div className="aspect-square rounded-xl border-2 border-dashed border-gray-200 overflow-hidden bg-gray-50 flex items-center justify-center">
              {illustPaths[i] ? (
                <img src={`${API_BASE}${illustPaths[i]}`} alt={scene.label} className="w-full h-full object-cover" />
              ) : illustStatuses[i].state === "loading" ? (
                <div className="text-center">
                  <Loader2 className="w-6 h-6 animate-spin text-gray-300 mx-auto" />
                  <span className="text-[10px] text-gray-400 mt-1 block">{scene.label}...</span>
                </div>
              ) : (
                <span className="text-gray-300 text-[10px]">{scene.label}</span>
              )}
            </div>
            <p className="text-[11px] text-center font-medium">{scene.label}</p>
            {illustStatuses[i].state === "done" && (
              <p className="text-[10px] text-center text-green-600">{illustStatuses[i].elapsed?.toFixed(1)}초</p>
            )}
            {illustStatuses[i].state === "error" && (
              <p className="text-[10px] text-center text-red-500 truncate" title={illustStatuses[i].error}>{illustStatuses[i].error}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ImageQualityTestPage() {
  const [samples, setSamples] = useState<string[]>([]);
  const [selectedPhoto, setSelectedPhoto] = useState("");
  const [selectedStyle, setSelectedStyle] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/api/test-image/samples`)
      .then((r) => r.json())
      .then((d) => {
        setSamples(d.files || []);
        if (d.files?.length > 0) setSelectedPhoto(d.files[0]);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">이미지 모델 비교 테스트</h1>
          <p className="text-gray-400 text-sm mt-1">
            같은 사진 · 같은 그림체로 두 모델을 나란히 비교
          </p>
        </div>

        {/* 사진 + 그림체 선택 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <section className="bg-white rounded-2xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold mb-3">사진 선택</h2>
            <div className="grid grid-cols-4 gap-2">
              {samples.map((file) => (
                <SamplePhoto
                  key={file}
                  file={file}
                  isSelected={selectedPhoto === file}
                  onClick={() => setSelectedPhoto(file)}
                />
              ))}
            </div>
          </section>

          <section className="bg-white rounded-2xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold mb-3">그림체 선택</h2>
            <div className="grid grid-cols-5 gap-2">
              {ART_STYLES.map((style) => {
                const isSelected = selectedStyle === style.id;
                const Icon = style.icon;
                return (
                  <button
                    key={style.id}
                    onClick={() => setSelectedStyle(style.id)}
                    className={`rounded-xl border-2 p-2 transition-all text-center ${
                      isSelected
                        ? "border-blue-500 ring-2 ring-blue-200 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <Icon className="w-6 h-6 mx-auto mb-1" style={{ color: style.color }} />
                    <p className="text-xs font-medium">{style.title}</p>
                  </button>
                );
              })}
            </div>
            <p className="text-xs text-gray-400 mt-3">
              직업: <strong>소방관</strong> / 이름: <strong>하준</strong>
            </p>
          </section>
        </div>

        {/* 모델 A */}
        <ModelRow
          config={MODEL_CONFIGS[0]}
          selectedPhoto={selectedPhoto}
          selectedStyle={selectedStyle}
          childName="하준"
          jobName="소방관"
          disabled={false}
        />

        {/* 모델 B */}
        <ModelRow
          config={MODEL_CONFIGS[1]}
          selectedPhoto={selectedPhoto}
          selectedStyle={selectedStyle}
          childName="하준"
          jobName="소방관"
          disabled={false}
        />
      </div>
    </div>
  );
}
