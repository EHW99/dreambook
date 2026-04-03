/**
 * API 클라이언트 — 백엔드 통신 유틸리티
 * Refresh Token은 httpOnly 쿠키로 관리 (XSS 방지)
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiError {
  detail: string;
}

class ApiClient {
  private getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private setAccessToken(token: string) {
    localStorage.setItem("access_token", token);
  }

  clearTokens() {
    localStorage.removeItem("access_token");
  }

  private async refreshAccessToken(): Promise<string | null> {
    try {
      // refresh_token은 httpOnly 쿠키로 자동 전송
      const res = await fetch(`${API_BASE}/api/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      });

      if (!res.ok) return null;

      const data = await res.json();
      this.setAccessToken(data.access_token);
      return data.access_token;
    } catch {
      return null;
    }
  }

  async request<T>(
    path: string,
    options: RequestInit = {},
    requireAuth = false
  ): Promise<{ data?: T; error?: string; status: number }> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (requireAuth) {
      const token = this.getAccessToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    let res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      credentials: "include",
    });

    // 401 또는 403이면 토큰 갱신 시도
    if ((res.status === 401 || res.status === 403) && requireAuth) {
      const newToken = await this.refreshAccessToken();
      if (newToken) {
        headers["Authorization"] = `Bearer ${newToken}`;
        res = await fetch(`${API_BASE}${path}`, {
          ...options,
          headers,
          credentials: "include",
        });
      }
    }

    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: "알 수 없는 오류가 발생했습니다" }));
      return {
        error: (body as ApiError).detail || "오류가 발생했습니다",
        status: res.status,
      };
    }

    const data = await res.json();
    return { data: data as T, status: res.status };
  }

  // === Auth API ===

  async signup(email: string, password: string) {
    return this.request<{ id: number; email: string }>(
      "/api/auth/signup",
      {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }
    );
  }

  async login(email: string, password: string) {
    const result = await this.request<{
      access_token: string;
      refresh_token: string;
      token_type: string;
    }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    if (result.data) {
      // access_token만 localStorage에 저장
      // refresh_token은 httpOnly 쿠키로 자동 관리됨
      this.setAccessToken(result.data.access_token);
    }

    return result;
  }

  async logout() {
    // 서버에 로그아웃 요청 (httpOnly 쿠키 삭제)
    await fetch(`${API_BASE}/api/auth/logout`, {
      method: "POST",
      credentials: "include",
    }).catch(() => {});
    this.clearTokens();
  }

  async getMe() {
    return this.request<{
      id: number;
      email: string;
      created_at: string;
    }>("/api/auth/me", {}, true);
  }

  // === Users API ===

  async changePassword(currentPassword: string, newPassword: string) {
    return this.request<{ message: string }>(
      "/api/users/password",
      {
        method: "PATCH",
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      },
      true
    );
  }

  async deleteAccount() {
    return this.request<{ message: string }>(
      "/api/users/me",
      { method: "DELETE" },
      true
    );
  }

  // === Photos API ===

  async uploadPhoto(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const token = this.getAccessToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    let res = await fetch(`${API_BASE}/api/photos`, {
      method: "POST",
      headers,
      body: formData,
      credentials: "include",
    });

    // 401이면 토큰 갱신 시도
    if (res.status === 401) {
      const newToken = await this.refreshAccessToken();
      if (newToken) {
        headers["Authorization"] = `Bearer ${newToken}`;
        res = await fetch(`${API_BASE}/api/photos`, {
          method: "POST",
          headers,
          body: formData,
          credentials: "include",
        });
      }
    }

    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: "알 수 없는 오류가 발생했습니다" }));
      return { error: (body as ApiError).detail || "오류가 발생했습니다", status: res.status };
    }

    const data = await res.json();
    return { data: data as PhotoItem, status: res.status };
  }

  async getPhotos() {
    return this.request<PhotoItem[]>("/api/photos", {}, true);
  }

  async deletePhoto(photoId: number) {
    return this.request<{ message: string }>(
      `/api/photos/${photoId}`,
      { method: "DELETE" },
      true
    );
  }

  isLoggedIn(): boolean {
    return !!this.getAccessToken();
  }
}

export interface PhotoItem {
  id: number;
  original_name: string;
  thumbnail_url: string;
  width: number;
  height: number;
  file_size: number;
  created_at: string;
}

export const apiClient = new ApiClient();
