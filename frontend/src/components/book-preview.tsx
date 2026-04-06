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
          fontFamily: "'Nanum Myeongjo',serif", fontSize: 24, fontWeight: 700,
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
    </>
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
        className="bg-white rounded-3xl p-7 w-full max-w-[560px] shadow-hover"
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

export default function BookPreview({ pages, title, childName, onTextSave }: BookPreviewProps) {
  const [si, setSi] = useState(0);  // spread index
  const [editPage, setEditPage] = useState<PageItem | null>(null);
  const boxRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(0.4);

  // 스프레드 만들기
  const spreads: PageItem[][] = [];
  if (pages.length > 0) spreads.push([pages[0]]);
  for (let i = 1; i < pages.length; i += 2) {
    spreads.push(i + 1 < pages.length ? [pages[i], pages[i + 1]] : [pages[i]]);
  }

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

  // 페이지 렌더
  function renderInner(p: PageItem) {
    switch (p.page_type) {
      case "title": return <TitlePage p={p} childName={childName} />;
      case "illustration": return <IllustPage p={p} />;
      case "story": return <StoryPage p={p} onEdit={() => setEditPage(p)} />;
      case "colophon": return <ColophonPage p={p} title={title} childName={childName} />;
      default: return null;
    }
  }

  const labels: Record<string, string> = {
    title: "제목", illustration: "그림", story: "이야기", colophon: "발행면",
  };

  return (
    <>
      <link href="https://fonts.googleapis.com/css2?family=Jua&family=Nanum+Myeongjo:wght@400;700&family=Nanum+Gothic:wght@400;700&display=swap" rel="stylesheet" />
      <style>{`
        .__story-wrap:hover .__edit-hint { opacity: 1 !important; }
        .__thumbs::-webkit-scrollbar { display: none; }
        .__thumbs { scrollbar-width: none; }
      `}</style>

      <div style={{ display: "flex", gap: 16, width: "100%", height: "calc(100vh - 200px)", minHeight: 400 }}>
        {/* 썸네일 */}
        <div className="__thumbs" style={{
          display: "flex", flexDirection: "column", gap: 6,
          overflowY: "auto", padding: "6px 2px", flexShrink: 0,
        }}>
          {spreads.map((sp, i) => {
            const active = i === si;
            return (
              <button key={i} onClick={() => setSi(i)} style={{
                width: sp.length === 1 ? 44 : 76, height: 40, flexShrink: 0,
                borderRadius: 6, border: active ? "2px solid #E8836B" : "2px solid transparent",
                background: active ? "#fff" : "#ece8e3", cursor: "pointer",
                display: "flex", gap: 1, padding: 2,
                opacity: active ? 1 : 0.55, transition: "all 0.15s",
              }}>
                {sp.map(p => {
                  const src = imgUrl((p.images.find(x => x.is_selected) || p.images[0])?.image_path);
                  const hasImg = (p.page_type === "illustration" || p.page_type === "colophon") && src;
                  return (
                    <div key={p.id} style={{
                      flex: 1, borderRadius: 3, overflow: "hidden",
                      background: hasImg ? undefined : "#ddd",
                      display: "flex", alignItems: "center", justifyContent: "center",
                    }}>
                      {hasImg
                        ? <img src={src} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} crossOrigin="anonymous" draggable={false} />
                        : <span style={{ fontSize: 7, color: "#999" }}>{p.page_number}</span>}
                    </div>
                  );
                })}
              </button>
            );
          })}
        </div>

        {/* 뷰어 */}
        <div ref={boxRef} style={{
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
              {cur.map(p => (
                <span key={p.id} style={{
                  background: "rgba(255,255,255,0.1)", padding: "2px 10px",
                  borderRadius: 99, color: "rgba(255,255,255,0.5)", fontSize: 11,
                }}>{labels[p.page_type] || `p${p.page_number}`}</span>
              ))}
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
              {/* 왼쪽 페이지 */}
              <div style={{
                position: "absolute", left: 0, top: 0, width: PW, height: PH,
                background: "#fff",
                boxShadow: "0 8px 40px rgba(0,0,0,0.35)",
                borderRadius: 3, overflow: "hidden",
              }}
              className={cur[0]?.page_type === "story" ? "__story-wrap" : ""}>
                {cur[0] && renderInner(cur[0])}
              </div>

              {/* 오른쪽 페이지 */}
              {cur[1] && (
                <div style={{
                  position: "absolute", left: PW + SPREAD_GAP, top: 0, width: PW, height: PH,
                  background: "#fff",
                  boxShadow: "0 8px 40px rgba(0,0,0,0.35)",
                  borderRadius: 3, overflow: "hidden",
                }}
                className={cur[1].page_type === "story" ? "__story-wrap" : ""}>
                  {renderInner(cur[1])}
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
