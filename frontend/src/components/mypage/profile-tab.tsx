"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  MailIcon,
  LockIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
} from "@/components/icons";

export function ProfileTab() {
  const { user, logout } = useAuth();
  const router = useRouter();

  // 비밀번호 변경 상태
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  // 탈퇴 다이얼로그 상태
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError("");
    setPasswordSuccess("");

    // 프론트엔드 검증
    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordError("모든 필드를 입력해주세요");
      return;
    }

    if (newPassword.length < 8) {
      setPasswordError("새 비밀번호는 8자 이상이어야 합니다");
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError("새 비밀번호가 일치하지 않습니다");
      return;
    }

    setIsChangingPassword(true);

    const result = await apiClient.changePassword(currentPassword, newPassword);

    if (result.error) {
      setPasswordError(result.error);
      setIsChangingPassword(false);
      return;
    }

    setPasswordSuccess("비밀번호가 변경되었습니다");
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setIsChangingPassword(false);
  };

  const handleDeleteAccount = async () => {
    setIsDeleting(true);

    const result = await apiClient.deleteAccount();

    if (result.error) {
      setIsDeleting(false);
      setShowDeleteDialog(false);
      return;
    }

    // 토큰 삭제 + 랜딩 페이지 이동
    logout();
    router.push("/");
  };

  return (
    <div className="space-y-8 max-w-lg mx-auto">
      {/* 이메일 (비활성) */}
      <section>
        <h3 className="text-lg font-bold text-text mb-4 flex items-center gap-2">
          <MailIcon className="w-5 h-5 text-primary" />
          이메일
        </h3>
        <Input
          type="email"
          value={user?.email || ""}
          disabled
          className="bg-secondary/20 cursor-not-allowed"
        />
        <p className="mt-1.5 text-xs text-text-lighter">
          이메일은 변경할 수 없습니다
        </p>
      </section>

      {/* 비밀번호 변경 */}
      <section>
        <h3 className="text-lg font-bold text-text mb-4 flex items-center gap-2">
          <LockIcon className="w-5 h-5 text-primary" />
          비밀번호 변경
        </h3>

        {passwordError && (
          <div className="mb-4 p-3 bg-error/10 border border-error/30 rounded-2xl text-sm text-error-dark">
            {passwordError}
          </div>
        )}

        {passwordSuccess && (
          <div className="mb-4 p-3 bg-success/20 border border-success rounded-2xl text-sm text-success-dark flex items-center gap-2">
            <CheckCircleIcon className="w-4 h-4" />
            {passwordSuccess}
          </div>
        )}

        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label
              htmlFor="current-password"
              className="block text-sm font-medium text-text mb-1.5"
            >
              현재 비밀번호
            </label>
            <Input
              id="current-password"
              type="password"
              placeholder="현재 비밀번호를 입력해주세요"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              disabled={isChangingPassword}
            />
          </div>

          <div>
            <label
              htmlFor="new-password"
              className="block text-sm font-medium text-text mb-1.5"
            >
              새 비밀번호
            </label>
            <Input
              id="new-password"
              type="password"
              placeholder="8자 이상 입력해주세요"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              disabled={isChangingPassword}
            />
          </div>

          <div>
            <label
              htmlFor="confirm-password"
              className="block text-sm font-medium text-text mb-1.5"
            >
              새 비밀번호 확인
            </label>
            <Input
              id="confirm-password"
              type="password"
              placeholder="새 비밀번호를 다시 입력해주세요"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={isChangingPassword}
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isChangingPassword}
          >
            {isChangingPassword ? "변경 중..." : "비밀번호 변경"}
          </Button>
        </form>
      </section>

      {/* 구분선 */}
      <hr className="border-secondary" />

      {/* 회원 탈퇴 */}
      <section>
        <h3 className="text-lg font-bold text-text mb-2 flex items-center gap-2">
          <AlertTriangleIcon className="w-5 h-5 text-error-dark" />
          회원 탈퇴
        </h3>
        <p className="text-sm text-text-light mb-4">
          탈퇴 시 모든 데이터(사진, 동화책, 주문 내역 등)가 즉시 삭제되며
          복구할 수 없습니다.
        </p>
        <Button
          variant="destructive"
          onClick={() => setShowDeleteDialog(true)}
        >
          회원 탈퇴
        </Button>
      </section>

      {/* 탈퇴 확인 다이얼로그 */}
      {showDeleteDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-3xl shadow-hover p-8 max-w-sm w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-error/20 flex items-center justify-center">
                <AlertTriangleIcon className="w-5 h-5 text-error-dark" />
              </div>
              <h4 className="text-lg font-bold text-text">회원 탈퇴</h4>
            </div>

            <p className="text-sm text-text-light mb-6">
              정말 탈퇴하시겠습니까? 모든 데이터가 삭제됩니다
            </p>

            <div className="flex gap-3">
              <Button
                variant="ghost"
                className="flex-1"
                onClick={() => setShowDeleteDialog(false)}
                disabled={isDeleting}
              >
                취소
              </Button>
              <Button
                variant="destructive"
                className="flex-1"
                onClick={handleDeleteAccount}
                disabled={isDeleting}
              >
                {isDeleting ? "처리 중..." : "탈퇴하기"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
