"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { User, Calendar } from "lucide-react";
import { Input } from "@/components/ui/input";

interface StepInfoInputProps {
  childName: string;
  childGender: string;
  childBirthDate: string;
  onUpdate: (data: { child_name?: string; child_gender?: string; child_birth_date?: string }) => void;
  onValidate: () => boolean;
}

export function StepInfoInput({
  childName,
  childGender,
  childBirthDate,
  onUpdate,
  onValidate,
}: StepInfoInputProps) {
  const [name, setName] = useState(childName);
  const [gender, setGender] = useState(childGender);
  const [birthDate, setBirthDate] = useState(childBirthDate);
  const [errors, setErrors] = useState<{ name?: string; gender?: string; birthDate?: string }>({});

  // 부모에게 변경 전달
  useEffect(() => {
    const data: { child_name?: string; child_gender?: string; child_birth_date?: string } = {};
    if (name.trim()) data.child_name = name.trim();
    if (gender) data.child_gender = gender;
    if (birthDate) data.child_birth_date = birthDate;
    onUpdate(data);
  }, [name, gender, birthDate]);

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

      {/* 성별 선택 */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-text">
          <User className="w-4 h-4 text-primary" />
          성별 <span className="text-error-dark">*</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {[
            { value: "male", label: "남자아이", emoji: "👦" },
            { value: "female", label: "여자아이", emoji: "👧" },
          ].map((opt) => {
            const isSelected = gender === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => {
                  setGender(opt.value);
                  setErrors((prev) => ({ ...prev, gender: undefined }));
                }}
                className={`h-11 rounded-2xl border-2 text-sm font-medium transition-all ${
                  isSelected
                    ? "border-primary bg-primary/5 text-text"
                    : "border-secondary bg-white hover:border-primary/50 text-text-light"
                }`}
              >
                {opt.emoji} {opt.label}
              </button>
            );
          })}
        </div>
        {errors.gender && <p className="text-xs text-error-dark">{errors.gender}</p>}
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
    </motion.div>
  );
}

// 유효성 검사 함수 (외부에서 호출 가능)
export function validateInfoInput(data: {
  childName: string;
  childGender: string;
  childBirthDate: string;
}): { valid: boolean; errors: { name?: string; gender?: string; birthDate?: string } } {
  const errors: { name?: string; gender?: string; birthDate?: string } = {};

  if (!data.childName.trim()) {
    errors.name = "아이 이름을 입력해주세요";
  } else if (data.childName.trim().length > 20) {
    errors.name = "아이 이름은 최대 20자까지 입력 가능합니다";
  }

  if (!data.childGender) {
    errors.gender = "성별을 선택해주세요";
  }

  if (!data.childBirthDate) {
    errors.birthDate = "생년월일을 선택해주세요";
  }

  return { valid: Object.keys(errors).length === 0, errors };
}
