"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Check, X, Type, Pencil } from "lucide-react";
import { PageItem } from "@/lib/api";

/* ================================================================
 *  동화책 미리보기 — 완전 새로 작성
 *
 *  원리:
 *  1) 고정 px 캔버스(978×1000.8)에 API 좌표 그대로 배치
 *  2) 스프레드(2장)는 absolute로 좌/우 배치 (flex 사용 안 함)
 *  3) 전체를 하나의 div에 담고 CSS zoom으로 축소
 *     zoom은 transform과 달리 레이아웃에 반영되므로 잘림 없음
 * ================================================================ */

const PW = 978;
const PH = 1000.8;
const SPREAD_GAP = 4;
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function imgUrl(path: string | null | undefined): string {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  if (path.startsWith("/uploads")) return `${API_BASE}${path}`;
  return `${API_BASE}/uploads/${path.split(/[/\\]/).pop()}`;
}

/* ── 페이지 렌더러 ── */

function TitlePage({ p, childName }: { p: PageItem; childName: string }) {
  return (
    <>
      <div style={{
        position: "absolute", left: 85.47, top: 407.25, width: 807.07, height: 97.08,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "'Jua', serif", fontSize: 50, fontWeight: 700, color: "#000",
        textAlign: "center",
      }}>
        {p.text_content || "제목"}
      </div>
      <div style={{
        position: "absolute", left: 357.13, top: 559.41, width: 263.73, height: 34.13,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "'Jua', sans-serif", fontSize: 20, color: "#000", textAlign: "center",
      }}>
        {childName}
      </div>
    </>
  );
}

function IllustPage({ p }: { p: PageItem }) {
  const src = imgUrl((p.images.find(i => i.is_selected) || p.images[0])?.image_path);
  const even = p.page_number % 2 === 0;
  // pageMargin: spine=25, head=30 → layout 좌표에 오프셋 적용
  const MX = 25, MY = 30;
  return (
    <>
      <div style={{
        position: "absolute", left: 14 + MX, top: 12.4 + MY, width: 900, height: 900,
        borderRadius: 20, overflow: "hidden", background: "#f5f0e8",
      }}>
        {src ? (
          <img src={src} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }}
            crossOrigin="anonymous" draggable={false} />
        ) : (
          <div style={{
            width: "100%", height: "100%",
            display: "flex", alignItems: "center", justifyContent: "center",
            background: "linear-gradient(135deg,#fef3e8,#fde8d8)",
            color: "#c4a97d", fontSize: 28, fontFamily: "'Jua',sans-serif",
          }}>
            일러스트 {p.page_number}
          </div>
        )}
      </div>
      <div style={{
        position: "absolute", left: even ? 51.45 : 855.17, top: 955.75,
        width: 71.38, height: 20.12,
        fontFamily: "'Nanum Gothic',sans-serif", fontSize: 12, color: "#000",
        textAlign: even ? "left" : "right",
      }}>
        {p.page_number}
      </div>
    </>
  );
}

function StoryPage({ p, onEdit }: { p: PageItem; onEdit: () => void }) {
  const odd = p.page_number % 2 === 1;
  // pageMargin: spine=25, head=30 → layout 좌표에 오프셋 적용
  const MX = 25, MY = 30;
  return (
    <>
      <div onClick={onEdit} style={{
        position: "absolute", left: 114 + MX, top: 62.4 + MY, width: 700, height: 800,
        display: "flex", alignItems: "center", justifyContent: "center",
        cursor: "pointer",
      }}>
        <p style={{
          fontFamily: "'Nanum Myeongjo',serif", fontSize: 30, fontWeight: 700,
          lineHeight: "60px", textAlign: "center", color: "#000",
          whiteSpace: "pre-wrap", wordBreak: "keep-all", margin: 0, padding: 16, width: "100%",
        }}>
          {p.text_content || "(클릭하여 편집)"}
        </p>
      </div>
      <div className="__edit-hint" style={{
        position: "absolute", bottom: 100, left: 0, width: PW,
        display: "flex", justifyContent: "center", opacity: 0, transition: "opacity 0.2s",
      }}>
        <span style={{
          background: "rgba(232,131,107,0.9)", color: "#fff",
          padding: "6px 16px", borderRadius: 20, fontSize: 13,
          display: "flex", alignItems: "center", gap: 6,
        }}>
          <Pencil size={13} /> 클릭하여 편집
        </span>
      </div>
      <div style={{
        position: "absolute", left: odd ? 855.17 : 51.45, top: 955.75,
        width: 71.38, height: 20.12,
        fontFamily: "'Nanum Gothic',sans-serif", fontSize: 12, color: "#000",
        textAlign: odd ? "right" : "left",
      }}>
        {p.page_number}
      </div>
    </>
  );
}

function ColophonPage({ p, title, childName }: { p: PageItem; title: string; childName: string }) {
  const src = imgUrl((p.images.find(i => i.is_selected) || p.images[0])?.image_path);
  const now = new Date();
  const date = `${now.getFullYear()}년 ${now.getMonth() + 1}월 ${now.getDate()}일`;
  return (
    <>
      <div style={{
        position: "absolute", left: 50, top: 277.08, width: 293.4, height: 293.4,
        borderRadius: 8, overflow: "hidden", background: "#f5f0e8",
      }}>
        {src && <img src={src} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }}
          crossOrigin="anonymous" draggable={false} />}
      </div>
      <div style={{
        position: "absolute", left: 50, top: 600.48, width: 652, height: 50,
        fontFamily: "'Nanum Gothic',sans-serif", fontSize: 20, color: "#000", lineHeight: "24px",
      }}>
        {title}
      </div>
      <div style={{
        position: "absolute", left: 50, top: 650.48, width: 350, height: 100,
        fontFamily: "'Nanum Gothic',sans-serif", fontSize: 12, color: "#000",
        lineHeight: "21px", whiteSpace: "pre-wrap",
      }}>
        {`발행일 : ${date}\n만든이 : ${childName || "AI 동화작가"}\n제작 : (주)스위트북`}
      </div>
      {/* Dreambook 로고 */}
      <div style={{
        position: "absolute", left: 53, top: 833, width: 268, height: 47,
        overflow: "hidden",
      }}>
        <img src="/logo.png" alt="Dreambook" style={{ width: "100%", height: "100%", objectFit: "contain" }}
          draggable={false} />
      </div>
    </>
  );
}

function CoverPage({ coverSrc, title, childName }: { coverSrc: string; title: string; childName: string }) {
  // 앞표지 상대좌표: 전체 x - 1060 (앞표지 시작점)
  // front-photo: (1248.9-1060, 155.6) = (188.9, 155.6) 636.3×636.3
  // front-subtitle: (1327.4-1060, 850.2) = (267.4, 850.2) 479.3×51.5
  // author: (1477.7-1060, 926.1) = (417.7, 926.1) 178.8×39.6
  return (
    <>
      <div style={{ position: "absolute", left: 0, top: 0, width: PW, height: PH, background: "#FFF8F0" }} />
      {/* 표지 사진 */}
      <div style={{
        position: "absolute", left: 189, top: 155.6, width: 636, height: 636,
        borderRadius: 20, overflow: "hidden", background: "#f5f0e8",
      }}>
        {coverSrc ? (
          <img src={coverSrc} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }}
            crossOrigin="anonymous" draggable={false} />
        ) : (
          <div style={{
            width: "100%", height: "100%",
            display: "flex", alignItems: "center", justifyContent: "center",
            background: "linear-gradient(135deg,#fef3e8,#fde8d8)",
            color: "#c4a97d", fontSize: 28, fontFamily: "'Jua',sans-serif",
          }}>
            표지
          </div>
        )}
      </div>
      {/* 제목 — subtitle */}
      <div style={{
        position: "absolute", left: 267, top: 850, width: 479, height: 52,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "'Jua', serif", fontSize: 40, fontWeight: 700, color: "#000",
        textAlign: "center",
      }}>
        {title}
      </div>
      {/* 저자 — author */}
      <div style={{
        position: "absolute", left: 418, top: 926, width: 179, height: 40,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "'Noto Sans KR', 'Nanum Gothic', sans-serif", fontSize: 16, color: "#666",
        textAlign: "center",
      }}>
        {childName}
      </div>
    </>
  );
}

function BackCoverPage({ title }: { title: string }) {
  // 뒷표지는 전체 표지의 왼쪽 영역 (x: 0~1013)
  // 하지만 미리보기에서는 1페이지=PW(978)로 렌더링하므로 좌표 그대로 사용
  // text-w2mbi50b (subtitle): (372.0, 453.4) 269.3×39.6 tvN즐거운이야기 Bold 16
  // graphic (로고): (372.0, 950.0) 269.3×50.0
  return (
    <div style={{
      position: "absolute", left: 0, top: 0, width: PW, height: PH,
      background: "#FFF8F0",
    }}>
      {/* 뒷표지 subtitle (책 제목) */}
      <div style={{
        position: "absolute", left: 372, top: 453, width: 269, height: 40,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "'Jua', sans-serif", fontSize: 16, fontWeight: 700, color: "#000",
        textAlign: "center",
      }}>
        {title}
      </div>
      {/* Dreambook 로고 */}
      <div style={{
        position: "absolute", left: 372, top: 950, width: 269, height: 50,
        overflow: "hidden",
      }}>
        <img src="/logo.png" alt="Dreambook" style={{ width: "100%", height: "100%", objectFit: "contain" }}
          draggable={false} />
      </div>
    </div>
  );
}

function BlankPage() {
  return (
    <div style={{
      position: "absolute", left: 0, top: 0, width: PW, height: PH,
      background: "#fff",
    }} />
  );
}

/* ── 편집 모달 ── */

function EditModal({ text, onSave, onClose }: {
  text: string; onSave: (t: string) => void; onClose: () => void;
}) {
  const [val, setVal] = useState(text);
  const ref = useRef<HTMLTextAreaElement>(null);
  useEffect(() => { ref.current?.focus(); }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center p-5"
    >
      <motion.div
        initial={{ scale: 0.95, y: 16 }} animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, y: 16 }}
        className="bg-white rounded-2xl sm:rounded-3xl p-5 sm:p-7 w-[92vw] sm:w-full max-w-[560px] shadow-hover"
      >
        <div className="flex items-center gap-3 mb-5">
          <div className="w-9 h-9 rounded-xl bg-primary-light flex items-center justify-center">
            <Type size={18} className="text-primary-dark" />
          </div>
          <span className="text-base font-bold text-text">이야기 편집</span>
        </div>
        <textarea
          ref={ref} value={val} onChange={e => setVal(e.target.value)}
          className="w-full h-[280px] border-2 border-secondary rounded-2xl p-5 font-display text-base leading-[2.2] text-center text-text resize-none outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/30"
        />
        <div className="flex gap-3 mt-5 justify-end">
          <button onClick={onClose}
            className="px-5 py-2.5 rounded-2xl bg-secondary-light border-none text-sm cursor-pointer font-semibold text-text-light hover:bg-secondary transition-colors flex items-center gap-1.5"
          >
            <X size={15} /> 취소
          </button>
          <button onClick={() => onSave(val)}
            className="px-5 py-2.5 rounded-2xl bg-primary border-none text-sm cursor-pointer font-semibold text-white hover:bg-primary-dark transition-colors flex items-center gap-1.5 shadow-soft"
          >
            <Check size={15} /> 저장
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ================================================================
 *  메인 컴포넌트
 * ================================================================ */

interface BookPreviewProps {
  pages: PageItem[];
  title: string;
  childName: string;
  onTextSave?: (pageId: number, text: string) => Promise<void>;
  coverImageUrl?: string;
}

export default function BookPreview({ pages, title, childName, onTextSave, coverImageUrl }: BookPreviewProps) {
  const [si, setSi] = useState(0);  // spread index
  const [editPage, setEditPage] = useState<PageItem | null>(null);
  const boxRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(0.4);

  // 스프레드 구성: 표지(단독) → [빈,간지] → [그림,스토리]×11 → [발행면,빈] → 뒷표지(단독)
  type SpreadItem = { type: "page"; data: PageItem } | { type: "cover" } | { type: "backcover" } | { type: "blank" };
  type Spread = SpreadItem[];
  const spreads: Spread[] = [];

  const coverSrc = imgUrl(coverImageUrl);

  // 1. 표지 (단독)
  spreads.push([{ type: "cover" }]);

  // 2. [빈, 간지(p1)]
  const titlePage = pages.find(p => p.page_type === "title");
  if (titlePage) {
    spreads.push([{ type: "blank" }, { type: "page", data: titlePage }]);
  }

  // 3. [그림, 스토리] 쌍
  const illustPages = pages.filter(p => p.page_type === "illustration").sort((a, b) => a.page_number - b.page_number);
  const storyPages = pages.filter(p => p.page_type === "story").sort((a, b) => a.page_number - b.page_number);
  for (let i = 0; i < illustPages.length; i++) {
    const left: SpreadItem = { type: "page", data: illustPages[i] };
    const right: SpreadItem = storyPages[i] ? { type: "page", data: storyPages[i] } : { type: "blank" };
    spreads.push([left, right]);
  }

  // 4. [발행면, 빈]
  const colophonPage = pages.find(p => p.page_type === "colophon");
  if (colophonPage) {
    spreads.push([{ type: "page", data: colophonPage }, { type: "blank" }]);
  }

  // 5. 뒷표지 (단독)
  spreads.push([{ type: "backcover" }]);

  const cur = spreads[si] || [];
  const single = cur.length === 1;
  const nativeW = single ? PW : PW * 2 + SPREAD_GAP;

  // zoom 계산
  useEffect(() => {
    function calc() {
      if (!boxRef.current) return;
      const { width: bw, height: bh } = boxRef.current.getBoundingClientRect();
      const zw = (bw - 100) / nativeW;
      const zh = (bh - 80) / PH;
      setZoom(Math.max(0.1, Math.min(zw, zh)));
    }
    calc();
    window.addEventListener("resize", calc);
    return () => window.removeEventListener("resize", calc);
  }, [si, nativeW]);

  // 키보드
  const next = () => setSi(i => Math.min(i + 1, spreads.length - 1));
  const prev = () => setSi(i => Math.max(i - 1, 0));
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if (editPage) return;
      if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); next(); }
      if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [editPage, spreads.length, si]);

  // 편집 저장
  const doSave = async (text: string) => {
    if (!editPage || !onTextSave) return;
    await onTextSave(editPage.id, text);
    setEditPage(null);
  };

  // SpreadItem 렌더
  function renderItem(item: SpreadItem) {
    switch (item.type) {
      case "cover": return <CoverPage coverSrc={coverSrc} title={title} childName={childName} />;
      case "backcover": return <BackCoverPage title={title} />;
      case "blank": return <BlankPage />;
      case "page": {
        const p = item.data;
        switch (p.page_type) {
          case "title": return <TitlePage p={p} childName={childName} />;
          case "illustration": return <IllustPage p={p} />;
          case "story": return <StoryPage p={p} onEdit={() => setEditPage(p)} />;
          case "colophon": return <ColophonPage p={p} title={title} childName={childName} />;
          default: return <BlankPage />;
        }
      }
    }
  }

  function itemLabel(item: SpreadItem): string {
    if (item.type === "cover") return "표지";
    if (item.type === "backcover") return "뒷표지";
    if (item.type === "blank") return "";
    const labels: Record<string, string> = { title: "제목", illustration: "그림", story: "이야기", colophon: "발행면" };
    return labels[item.data.page_type] || `p${item.data.page_number}`;
  }

  return (
    <>
      <link href="https://fonts.googleapis.com/css2?family=Jua&family=Nanum+Myeongjo:wght@400;700&family=Nanum+Gothic:wght@400;700&display=swap" rel="stylesheet" />
      <style>{`
        .__story-wrap:hover .__edit-hint { opacity: 1 !important; }
        .__bpv-thumbs::-webkit-scrollbar { display: none; }
        .__bpv-thumbs { scrollbar-width: none; }
        @media (max-width: 767px) {
          .__bpv-layout { flex-direction: column !important; height: auto !important; }
          .__bpv-viewer { min-height: 50vh !important; }
          .__bpv-sidebar { flex-direction: row !important; overflow-x: auto !important; overflow-y: hidden !important; max-height: none !important; padding: 8px 4px !important; }
          .__bpv-sidebar button { flex-shrink: 0 !important; }
        }
      `}</style>

      <div className="__bpv-layout" style={{ display: "flex", gap: 12, width: "100%", height: "calc(100vh - 200px)", minHeight: 400 }}>
        {/* 뷰어 — 왼쪽 (모바일: 위) */}
        <div ref={boxRef} className="__bpv-viewer" style={{
          flex: 1, display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center",
          background: "#2a2420", borderRadius: 16,
          position: "relative", overflow: "hidden", minWidth: 0,
        }}>
          {/* 상단 */}
          <div style={{
            position: "absolute", top: 0, left: 0, right: 0, zIndex: 5,
            display: "flex", justifyContent: "space-between", padding: "10px 18px",
          }}>
            <div style={{ display: "flex", gap: 6 }}>
              {cur.map((item, idx) => {
                const label = itemLabel(item);
                return label ? (
                  <span key={idx} style={{
                    background: "rgba(255,255,255,0.1)", padding: "2px 10px",
                    borderRadius: 99, color: "rgba(255,255,255,0.5)", fontSize: 11,
                  }}>{label}</span>
                ) : null;
              })}
            </div>
            <span style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}>
              {si + 1} / {spreads.length}
            </span>
          </div>

          {/* 이전 */}
          <button onClick={prev} disabled={si === 0} style={{
            position: "absolute", left: 8, top: "50%", transform: "translateY(-50%)", zIndex: 5,
            width: 36, height: 36, borderRadius: 99,
            display: "flex", alignItems: "center", justifyContent: "center",
            background: si === 0 ? "transparent" : "rgba(255,255,255,0.08)",
            border: "none", color: si === 0 ? "rgba(255,255,255,0.1)" : "rgba(255,255,255,0.7)",
            cursor: si === 0 ? "default" : "pointer",
          }}><ChevronLeft size={22} /></button>

          {/* ★ 스프레드 — 래퍼(레이아웃) + 내부(transform) */}
          {/* 바깥: 축소된 크기로 레이아웃 공간 확보 */}
          <div style={{
            width: nativeW * zoom,
            height: PH * zoom,
            position: "relative",
            overflow: "hidden",
          }}>
            {/* 안쪽: position absolute로 레이아웃 영향 차단 */}
            <div style={{
              width: nativeW,
              height: PH,
              transform: `scale(${zoom})`,
              transformOrigin: "top left",
              position: "absolute",
              top: 0,
              left: 0,
            }}>
              {/* 왼쪽 (또는 단독) 페이지 */}
              <div style={{
                position: "absolute", left: 0, top: 0, width: PW, height: PH,
                background: "#fff",
                boxShadow: "0 8px 40px rgba(0,0,0,0.35)",
                borderRadius: 3, overflow: "hidden",
              }}
              className={cur[0]?.type === "page" && cur[0].data.page_type === "story" ? "__story-wrap" : ""}>
                {cur[0] && renderItem(cur[0])}
              </div>

              {/* 오른쪽 페이지 */}
              {cur[1] && (
                <div style={{
                  position: "absolute", left: PW + SPREAD_GAP, top: 0, width: PW, height: PH,
                  background: "#fff",
                  boxShadow: "0 8px 40px rgba(0,0,0,0.35)",
                  borderRadius: 3, overflow: "hidden",
                }}
                className={cur[1].type === "page" && cur[1].data.page_type === "story" ? "__story-wrap" : ""}>
                  {renderItem(cur[1])}
                </div>
              )}
            </div>
          </div>

          {/* 다음 */}
          <button onClick={next} disabled={si === spreads.length - 1} style={{
            position: "absolute", right: 8, top: "50%", transform: "translateY(-50%)", zIndex: 5,
            width: 36, height: 36, borderRadius: 99,
            display: "flex", alignItems: "center", justifyContent: "center",
            background: si === spreads.length - 1 ? "transparent" : "rgba(255,255,255,0.08)",
            border: "none",
            color: si === spreads.length - 1 ? "rgba(255,255,255,0.1)" : "rgba(255,255,255,0.7)",
            cursor: si === spreads.length - 1 ? "default" : "pointer",
          }}><ChevronRight size={22} /></button>

          {/* 인디케이터 */}
          <div style={{
            position: "absolute", bottom: 10, left: 0, right: 0,
            display: "flex", justifyContent: "center", gap: 5,
          }}>
            {spreads.length <= 16 ? spreads.map((_, i) => (
              <button key={i} onClick={() => setSi(i)} style={{
                width: i === si ? 20 : 6, height: 6, borderRadius: 99,
                border: "none", cursor: "pointer",
                background: i === si ? "#E8836B" : "rgba(255,255,255,0.2)",
                transition: "all 0.2s",
              }} />
            )) : (
              <span style={{ color: "rgba(255,255,255,0.5)", fontSize: 12 }}>
                {si + 1} / {spreads.length}
              </span>
            )}
          </div>
        </div>

        {/* 썸네일 사이드바 — 오른쪽 (모바일: 아래) */}
        <div className="__bpv-thumbs __bpv-sidebar" style={{
          display: "flex", flexDirection: "column", gap: 4,
          overflowY: "auto", padding: "4px", flexShrink: 0,
          maxHeight: "100%", width: 90,
        }}>
          {(() => {
            // 단일 항목 리스트: 표지, 그림1~11(+페이지번호), 발행면, 뒷표지
            type ThumbItem = { label: string; src: string; spreadIdx: number };
            const items: ThumbItem[] = [];

            // 표지
            items.push({ label: "표지", src: coverSrc, spreadIdx: 0 });

            // 일러스트 페이지들 — 해당 스프레드 인덱스 찾기
            const illustPages2 = pages.filter(p => p.page_type === "illustration").sort((a, b) => a.page_number - b.page_number);
            illustPages2.forEach((p, idx) => {
              const src2 = imgUrl((p.images.find(x => x.is_selected) || p.images[0])?.image_path);
              // 스프레드: [빈,간지]=1, [그림1,스토리1]=2, [그림2,스토리2]=3, ...
              const spreadIdx2 = idx + 2;
              items.push({ label: `${p.page_number}p`, src: src2, spreadIdx: spreadIdx2 });
            });

            // 발행면
            const colIdx = spreads.length - 2; // [발행면, 빈]
            items.push({ label: "발행면", src: "", spreadIdx: colIdx });

            // 뒷표지
            items.push({ label: "뒷표지", src: "", spreadIdx: spreads.length - 1 });

            return items.map((item, i) => {
              const active = si === item.spreadIdx;
              return (
                <button key={i} onClick={() => setSi(item.spreadIdx)} style={{
                  width: "100%", flexShrink: 0, borderRadius: 6,
                  border: active ? "2px solid #E8836B" : "2px solid transparent",
                  background: active ? "#fff" : "#ece8e3", cursor: "pointer",
                  padding: 2, opacity: active ? 1 : 0.55, transition: "all 0.15s",
                  display: "flex", flexDirection: "column", alignItems: "center", gap: 2,
                }}>
                  <div style={{
                    width: "100%", aspectRatio: "1/1", borderRadius: 4, overflow: "hidden",
                    background: item.src ? undefined : "#ddd",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    {item.src
                      ? <img src={item.src} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} crossOrigin="anonymous" draggable={false} />
                      : <span style={{ fontSize: 9, color: "#999" }}>{item.label}</span>}
                  </div>
                  <span style={{ fontSize: 9, color: active ? "#E8836B" : "#999", lineHeight: 1 }}>{item.label}</span>
                </button>
              );
            });
          })()}
        </div>
      </div>

      {/* 편집 모달 */}
      <AnimatePresence>
        {editPage && (
          <EditModal text={editPage.text_content || ""} onSave={doSave} onClose={() => setEditPage(null)} />
        )}
      </AnimatePresence>
    </>
  );
}
