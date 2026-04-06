"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { apiClient, PhotoItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { PhotoLightbox } from "@/components/ui/photo-lightbox";
import {
  CameraIcon,
  AlertTriangleIcon,
} from "@/components/icons";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

// 아이콘: 업로드
function UploadIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

// 아이콘: 휴지통
function TrashIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <line x1="10" y1="11" x2="10" y2="17" />
      <line x1="14" y1="11" x2="14" y2="17" />
    </svg>
  );
}

// 아이콘: 이미지
function ImageIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
      <circle cx="9" cy="9" r="2" />
      <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
    </svg>
  );
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
    if (result.data) {
      setPhotos(result.data);
    }
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
      const file = files[i];
      const result = await apiClient.uploadPhoto(file);
      if (result.error) {
        setError(result.error);
        break;
      }
    }

    setIsUploading(false);
    await loadPhotos();

    // 파일 인풋 리셋
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
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

  // 드래그앤드롭 핸들러
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

  // 로딩 중
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="mt-4 text-sm text-text-light">사진을 불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 에러 메시지 */}
      {error && (
        <div className="p-3 bg-error/10 border border-error/30 rounded-2xl text-sm text-error-dark flex items-center gap-2">
          <AlertTriangleIcon className="w-4 h-4 flex-shrink-0" />
          {error}
          <button
            onClick={() => setError("")}
            className="ml-auto text-error-dark hover:text-error font-bold"
          >
            &times;
          </button>
        </div>
      )}

      {/* 헤더 영역: 제목 + 업로드 버튼 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CameraIcon className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-bold text-text">
            아이 사진 ({photos.length}/20)
          </h3>
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
          >
            <UploadIcon className="w-4 h-4 mr-2" />
            {isUploading ? "업로드 중..." : "사진 추가"}
          </Button>
        </div>
      </div>

      {/* 빈 상태 */}
      {photos.length === 0 ? (
        <div
          className={`
            flex flex-col items-center justify-center py-16 border-2 border-dashed rounded-3xl transition-colors cursor-pointer
            ${isDragOver ? "border-primary bg-primary/5" : "border-secondary hover:border-primary/50"}
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="w-16 h-16 rounded-full bg-secondary/50 flex items-center justify-center mb-4">
            <ImageIcon className="w-8 h-8 text-text-light" />
          </div>
          <p className="text-lg font-medium text-text mb-2">
            등록된 사진이 없어요
          </p>
          <p className="text-sm text-text-light text-center max-w-xs">
            아이의 사진을 등록하면 동화책 캐릭터를 만들 수 있어요.
            <br />
            JPG, PNG, WebP 형식 (512x512 이상, 10MB 이하)
          </p>
          <Button className="mt-6" variant="outline" size="sm">
            <UploadIcon className="w-4 h-4 mr-2" />
            사진 업로드하기
          </Button>
        </div>
      ) : (
        /* 사진 그리드 */
        <div
          className={`
            relative rounded-3xl transition-colors
            ${isDragOver ? "ring-2 ring-primary ring-offset-2" : ""}
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {isDragOver && (
            <div className="absolute inset-0 bg-primary/10 rounded-3xl z-10 flex items-center justify-center">
              <p className="text-primary font-medium">여기에 사진을 놓아주세요</p>
            </div>
          )}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {photos.map((photo, index) => (
              <div
                key={photo.id}
                className="group relative bg-white rounded-2xl shadow-card overflow-hidden transition-shadow hover:shadow-hover"
              >
                {/* 썸네일 — 클릭 시 크게보기 */}
                <button
                  type="button"
                  onClick={() => setLightboxIndex(index)}
                  className="w-full aspect-square bg-secondary/20 overflow-hidden cursor-pointer"
                >
                  <img
                    src={`${API_BASE}${photo.thumbnail_url}`}
                    alt={photo.original_name}
                    className="w-full h-full object-cover transition-transform group-hover:scale-105"
                    loading="lazy"
                  />
                </button>

                {/* 삭제 버튼 (hover 시 표시) */}
                <button
                  onClick={() => setDeleteTarget(photo)}
                  className="absolute top-2 right-2 w-8 h-8 bg-white/80 hover:bg-error hover:text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all shadow-sm"
                  title="삭제"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>

                {/* 파일 정보 */}
                <div className="p-3">
                  <p className="text-xs font-medium text-text truncate">
                    {photo.original_name}
                  </p>
                  <div className="flex items-center justify-between mt-1">
                    <p className="text-xs text-text-lighter">
                      {formatDate(photo.created_at)}
                    </p>
                    <p className="text-xs text-text-lighter">
                      {formatFileSize(photo.file_size)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 사진 크게보기 라이트박스 */}
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

      {/* 삭제 확인 다이얼로그 */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-3xl shadow-hover p-8 max-w-sm w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-error/20 flex items-center justify-center">
                <TrashIcon className="w-5 h-5 text-error-dark" />
              </div>
              <h4 className="text-lg font-bold text-text">사진 삭제</h4>
            </div>

            <p className="text-sm text-text-light mb-2">
              &quot;{deleteTarget.original_name}&quot;을(를) 삭제하시겠습니까?
            </p>
            <p className="text-xs text-text-lighter mb-6">
              삭제된 사진은 복구할 수 없습니다.
            </p>

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
          </div>
        </div>
      )}
    </div>
  );
}
