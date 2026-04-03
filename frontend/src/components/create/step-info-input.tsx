"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Camera, Plus, Check, User, Calendar, ImageIcon } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { apiClient, PhotoItem } from "@/lib/api";

interface StepInfoInputProps {
  childName: string;
  childBirthDate: string;
  photoId: number | null;
  onUpdate: (data: { child_name?: string; child_birth_date?: string; photo_id?: number }) => void;
  onValidate: () => boolean;
}

export function StepInfoInput({
  childName,
  childBirthDate,
  photoId,
  onUpdate,
  onValidate,
}: StepInfoInputProps) {
  const [name, setName] = useState(childName);
  const [birthDate, setBirthDate] = useState(childBirthDate);
  const [selectedPhotoId, setSelectedPhotoId] = useState<number | null>(photoId);
  const [photos, setPhotos] = useState<PhotoItem[]>([]);
  const [loadingPhotos, setLoadingPhotos] = useState(true);
  const [errors, setErrors] = useState<{ name?: string; birthDate?: string; photo?: string }>({});
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadPhotos();
  }, []);

  // 부모에게 변경 전달
  useEffect(() => {
    const data: { child_name?: string; child_birth_date?: string; photo_id?: number } = {};
    if (name.trim()) data.child_name = name.trim();
    if (birthDate) data.child_birth_date = birthDate;
    if (selectedPhotoId) data.photo_id = selectedPhotoId;
    onUpdate(data);
  }, [name, birthDate, selectedPhotoId]);

  async function loadPhotos() {
    const result = await apiClient.getPhotos();
    if (result.data) {
      setPhotos(result.data);
    }
    setLoadingPhotos(false);
  }

  async function handlePhotoUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const result = await apiClient.uploadPhoto(file);
    if (result.data) {
      setPhotos((prev) => [result.data!, ...prev]);
      setSelectedPhotoId(result.data.id);
      setErrors((prev) => ({ ...prev, photo: undefined }));
    } else if (result.error) {
      setErrors((prev) => ({ ...prev, photo: result.error }));
    }
    setUploading(false);
    // input 초기화
    e.target.value = "";
  }

  // 유효성 검사 — 부모에서 호출
  useEffect(() => {
    // onValidate를 오버라이드
    const originalValidate = onValidate;
    // 이 컴포넌트에서 validate를 정의하지만 부모에게 콜백으로 넘기는 구조
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-8"
    >
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-text mb-2">아이 정보를 입력해주세요</h2>
        <p className="text-text-light">동화책의 주인공이 될 아이의 정보예요</p>
      </div>

      {/* 이름 입력 */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-text">
          <User className="w-4 h-4 text-primary" />
          아이 이름 <span className="text-error-dark">*</span>
        </label>
        <Input
          placeholder="아이 이름을 입력해주세요"
          value={name}
          maxLength={20}
          onChange={(e) => {
            setName(e.target.value);
            if (e.target.value.trim()) {
              setErrors((prev) => ({ ...prev, name: undefined }));
            }
          }}
          error={errors.name}
        />
        <p className="text-xs text-text-lighter text-right">{name.length}/20</p>
      </div>

      {/* 생년월일 */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-text">
          <Calendar className="w-4 h-4 text-primary" />
          생년월일 <span className="text-error-dark">*</span>
        </label>
        <input
          type="date"
          value={birthDate}
          max={new Date().toISOString().split("T")[0]}
          onChange={(e) => {
            setBirthDate(e.target.value);
            if (e.target.value) {
              setErrors((prev) => ({ ...prev, birthDate: undefined }));
            }
          }}
          className={`flex h-11 w-full rounded-2xl border-2 bg-white px-4 py-2 text-sm transition-colors
            focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary
            ${errors.birthDate ? "border-error" : "border-secondary hover:border-primary/50"}`}
        />
        {errors.birthDate && <p className="text-xs text-error-dark">{errors.birthDate}</p>}
      </div>

      {/* 사진 선택 */}
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm font-medium text-text">
          <Camera className="w-4 h-4 text-primary" />
          아이 사진
        </label>
        <p className="text-xs text-text-light">
          등록된 사진에서 선택하거나 새로 업로드해주세요
        </p>

        {/* 사진 그리드 */}
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
          {/* 업로드 버튼 */}
          <label className="aspect-square rounded-2xl border-2 border-dashed border-secondary hover:border-primary cursor-pointer flex flex-col items-center justify-center gap-1 transition-colors bg-white/50">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={handlePhotoUpload}
              disabled={uploading}
            />
            {uploading ? (
              <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full" />
            ) : (
              <>
                <Plus className="w-6 h-6 text-text-lighter" />
                <span className="text-[10px] text-text-lighter">새 사진</span>
              </>
            )}
          </label>

          {/* 기존 사진 */}
          {loadingPhotos ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="aspect-square rounded-2xl bg-secondary/30 animate-pulse" />
            ))
          ) : (
            photos.map((photo) => (
              <motion.button
                key={photo.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  setSelectedPhotoId(photo.id);
                  setErrors((prev) => ({ ...prev, photo: undefined }));
                }}
                className={`relative aspect-square rounded-2xl overflow-hidden border-2 transition-all ${
                  selectedPhotoId === photo.id
                    ? "border-primary ring-2 ring-primary/30"
                    : "border-transparent hover:border-secondary"
                }`}
              >
                <img
                  src={photo.thumbnail_url}
                  alt={photo.original_name}
                  className="w-full h-full object-cover"
                />
                {selectedPhotoId === photo.id && (
                  <div className="absolute inset-0 bg-primary/20 flex items-center justify-center">
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  </div>
                )}
              </motion.button>
            ))
          )}
        </div>

        {errors.photo && <p className="text-xs text-error-dark">{errors.photo}</p>}

        {!loadingPhotos && photos.length === 0 && (
          <div className="text-center py-6 bg-secondary/10 rounded-2xl">
            <ImageIcon className="w-8 h-8 text-text-lighter mx-auto mb-2" />
            <p className="text-sm text-text-light">등록된 사진이 없어요</p>
            <p className="text-xs text-text-lighter mt-1">위 버튼으로 사진을 업로드해주세요</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}

// 유효성 검사 함수 (외부에서 호출 가능)
export function validateInfoInput(data: {
  childName: string;
  childBirthDate: string;
}): { valid: boolean; errors: { name?: string; birthDate?: string } } {
  const errors: { name?: string; birthDate?: string } = {};

  if (!data.childName.trim()) {
    errors.name = "아이 이름을 입력해주세요";
  } else if (data.childName.trim().length > 20) {
    errors.name = "아이 이름은 최대 20자까지 입력 가능합니다";
  }

  if (!data.childBirthDate) {
    errors.birthDate = "생년월일을 선택해주세요";
  }

  return { valid: Object.keys(errors).length === 0, errors };
}
