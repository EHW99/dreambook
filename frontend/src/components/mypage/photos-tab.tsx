"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  Trash2,
  ImageIcon,
  Camera,
  AlertTriangle,
  X,
  ZoomIn,
} from "lucide-react";
import { apiClient, PhotoItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { PhotoLightbox } from "@/components/ui/photo-lightbox";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

export function PhotosTab() {
  const [photos, setPhotos] = useState<PhotoItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<PhotoItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadPhotos = useCallback(async () => {
    setIsLoading(true);
    const result = await apiClient.getPhotos();
    if (result.data) setPhotos(result.data);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    loadPhotos();
  }, [loadPhotos]);

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setError("");
    setIsUploading(true);
    for (let i = 0; i < files.length; i++) {
      const result = await apiClient.uploadPhoto(files[i]);
      if (result.error) {
        setError(result.error);
        break;
      }
    }
    setIsUploading(false);
    await loadPhotos();
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    const result = await apiClient.deletePhoto(deleteTarget.id);
    if (result.error) {
      setError(result.error);
    } else {
      setPhotos((prev) => prev.filter((p) => p.id !== deleteTarget.id));
    }
    setIsDeleting(false);
    setDeleteTarget(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };
  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    handleUpload(e.dataTransfer.files);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="mt-4 text-sm text-text-light">사진을 불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* 에러 */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="p-3 bg-error/10 border border-error/30 rounded-2xl text-sm text-error-dark flex items-center gap-2"
          >
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span className="flex-1">{error}</span>
            <button onClick={() => setError("")} className="hover:text-error">
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Camera className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-bold text-text">
            아이 사진
          </h3>
          <span className="text-sm text-text-lighter">
            {photos.length}/20
          </span>
        </div>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            multiple
            className="hidden"
            onChange={(e) => handleUpload(e.target.files)}
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading || photos.length >= 20}
            size="sm"
            className="gap-2"
          >
            <Upload className="w-4 h-4" />
            {isUploading ? "업로드 중..." : "사진 추가"}
          </Button>
        </div>
      </div>

      {/* 빈 상태 */}
      {photos.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`
            flex flex-col items-center justify-center py-16 border-2 border-dashed rounded-3xl transition-all cursor-pointer
            ${isDragOver ? "border-primary bg-primary/5 scale-[1.01]" : "border-secondary hover:border-primary/40"}
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center mb-4">
            <ImageIcon className="w-8 h-8 text-text-light" />
          </div>
          <p className="text-base font-medium text-text mb-1">
            등록된 사진이 없어요
          </p>
          <p className="text-sm text-text-light text-center max-w-xs mb-5">
            아이의 사진을 등록하면 동화책 캐릭터를 만들 수 있어요
          </p>
          <div className="flex flex-col items-center gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <Upload className="w-4 h-4" />
              사진 업로드하기
            </Button>
            <p className="text-xs text-text-lighter">
              JPG, PNG, WebP · 512×512 이상 · 10MB 이하
            </p>
          </div>
        </motion.div>
      ) : (
        /* 사진 그리드 */
        <div
          className={`relative rounded-3xl transition-all ${
            isDragOver ? "ring-2 ring-primary ring-offset-2" : ""
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {/* 드래그 오버레이 */}
          <AnimatePresence>
            {isDragOver && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-primary/10 backdrop-blur-sm rounded-3xl z-10 flex items-center justify-center"
              >
                <div className="text-center">
                  <Upload className="w-8 h-8 text-primary mx-auto mb-2" />
                  <p className="text-primary font-medium">여기에 놓아주세요</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 sm:gap-4">
            {photos.map((photo, index) => (
              <motion.div
                key={photo.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.03 }}
                className="group relative rounded-2xl overflow-hidden shadow-soft hover:shadow-card transition-shadow bg-white"
              >
                {/* 이미지 */}
                <button
                  type="button"
                  onClick={() => setLightboxIndex(index)}
                  className="w-full aspect-square bg-secondary/20 overflow-hidden cursor-pointer"
                >
                  <img
                    src={`${API_BASE}${photo.thumbnail_url}`}
                    alt={photo.original_name}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    loading="lazy"
                  />
                </button>

                {/* hover/mobile 오버레이 */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-200 pointer-events-none" />

                {/* 하단 정보 (hover 시) */}
                <div className="absolute bottom-0 left-0 right-0 p-2.5 translate-y-full group-hover:translate-y-0 transition-transform duration-200">
                  <p className="text-[11px] text-white/90 truncate font-medium">
                    {photo.original_name}
                  </p>
                  <p className="text-[10px] text-white/60">
                    {formatDate(photo.created_at)} · {formatFileSize(photo.file_size)}
                  </p>
                </div>

                {/* 확대 버튼 (hover 시) */}
                <button
                  onClick={() => setLightboxIndex(index)}
                  className="absolute top-2 left-2 w-7 h-7 bg-white/80 backdrop-blur-sm rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-sm hover:bg-white"
                >
                  <ZoomIn className="w-3.5 h-3.5 text-text" />
                </button>

                {/* 삭제 버튼 — 모바일은 항상 표시, 데스크톱은 hover */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteTarget(photo);
                  }}
                  className="absolute top-2 right-2 w-7 h-7 bg-white/80 backdrop-blur-sm hover:bg-error hover:text-white rounded-lg flex items-center justify-center opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-all shadow-sm"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* 업로드 안내 (사진 있을 때) */}
      {photos.length > 0 && photos.length < 20 && (
        <p className="text-xs text-text-lighter text-center">
          JPG, PNG, WebP · 512×512 이상 · 10MB 이하 · 드래그 앤 드롭으로도 추가할 수 있어요
        </p>
      )}

      {/* 라이트박스 */}
      {lightboxIndex !== null && (
        <PhotoLightbox
          images={photos.map((p) => ({
            src: `${API_BASE}${p.thumbnail_url}`,
            alt: p.original_name,
          }))}
          initialIndex={lightboxIndex}
          onClose={() => setLightboxIndex(null)}
        />
      )}

      {/* 삭제 확인 모달 */}
      <AnimatePresence>
        {deleteTarget && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
            onClick={() => !isDeleting && setDeleteTarget(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-3xl shadow-hover p-6 max-w-sm w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-error/10 flex items-center justify-center">
                  <Trash2 className="w-5 h-5 text-error-dark" />
                </div>
                <div>
                  <h4 className="text-base font-bold text-text">사진 삭제</h4>
                  <p className="text-xs text-text-lighter">삭제된 사진은 복구할 수 없습니다</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl mb-5">
                <img
                  src={`${API_BASE}${deleteTarget.thumbnail_url}`}
                  alt={deleteTarget.original_name}
                  className="w-12 h-12 rounded-lg object-cover"
                />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-text truncate">
                    {deleteTarget.original_name}
                  </p>
                  <p className="text-xs text-text-lighter">
                    {formatFileSize(deleteTarget.file_size)}
                  </p>
                </div>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="ghost"
                  className="flex-1"
                  onClick={() => setDeleteTarget(null)}
                  disabled={isDeleting}
                >
                  취소
                </Button>
                <Button
                  variant="destructive"
                  className="flex-1"
                  onClick={handleDelete}
                  disabled={isDeleting}
                >
                  {isDeleting ? "삭제 중..." : "삭제하기"}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
