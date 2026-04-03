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

  // === Vouchers API ===

  async getVouchers() {
    return this.request<VoucherItem[]>("/api/vouchers", {}, true);
  }

  async purchaseVoucher(voucherType: string) {
    return this.request<VoucherItem>(
      "/api/vouchers/purchase",
      {
        method: "POST",
        body: JSON.stringify({ voucher_type: voucherType }),
      },
      true
    );
  }

  // === Books API ===

  async getBooks() {
    return this.request<BookListItem[]>("/api/books", {}, true);
  }

  async createBook(voucherId: number) {
    return this.request<BookItem>(
      "/api/books",
      {
        method: "POST",
        body: JSON.stringify({ voucher_id: voucherId }),
      },
      true
    );
  }

  async getBook(bookId: number) {
    return this.request<BookItem>(`/api/books/${bookId}`, {}, true);
  }

  async updateBook(bookId: number, data: BookUpdateData) {
    return this.request<BookItem>(
      `/api/books/${bookId}`,
      {
        method: "PATCH",
        body: JSON.stringify(data),
      },
      true
    );
  }

  async deleteBook(bookId: number) {
    return this.request<{ message: string }>(
      `/api/books/${bookId}`,
      { method: "DELETE" },
      true
    );
  }

  // === Character API ===

  async createCharacter(bookId: number) {
    return this.request<CharacterSheetItem>(
      `/api/books/${bookId}/character`,
      { method: "POST" },
      true
    );
  }

  async getCharacters(bookId: number) {
    return this.request<CharacterSheetItem[]>(
      `/api/books/${bookId}/characters`,
      {},
      true
    );
  }

  async selectCharacter(bookId: number, charId: number) {
    return this.request<CharacterSheetItem>(
      `/api/books/${bookId}/character/${charId}/select`,
      { method: "PATCH" },
      true
    );
  }

  // === Generate API ===

  async generateBook(bookId: number) {
    return this.request<GenerateResult>(
      `/api/books/${bookId}/generate`,
      { method: "POST" },
      true
    );
  }

  async getPages(bookId: number) {
    return this.request<PageItem[]>(
      `/api/books/${bookId}/pages`,
      {},
      true
    );
  }

  async updatePageText(bookId: number, pageId: number, textContent: string) {
    return this.request<PageItem>(
      `/api/books/${bookId}/pages/${pageId}`,
      {
        method: "PATCH",
        body: JSON.stringify({ text_content: textContent }),
      },
      true
    );
  }

  async regenerateStory(bookId: number) {
    return this.request<RegenerateStoryResult>(
      `/api/books/${bookId}/regenerate-story`,
      { method: "POST" },
      true
    );
  }

  async regenerateImage(bookId: number, pageId: number) {
    return this.request<RegenerateImageResult>(
      `/api/books/${bookId}/pages/${pageId}/regenerate-image`,
      { method: "POST" },
      true
    );
  }

  async getPageImages(bookId: number, pageId: number) {
    return this.request<PageImageItem[]>(
      `/api/books/${bookId}/pages/${pageId}/images`,
      {},
      true
    );
  }

  async selectPageImage(bookId: number, pageId: number, imageId: number) {
    return this.request<{ id: number; is_selected: boolean }>(
      `/api/books/${bookId}/pages/${pageId}/images/${imageId}/select`,
      { method: "PATCH" },
      true
    );
  }

  // === Order API ===

  async getEstimate(bookId: number) {
    return this.request<EstimateResult>(
      `/api/books/${bookId}/estimate`,
      { method: "POST" },
      true
    );
  }

  async createOrder(bookId: number, shipping: ShippingData) {
    return this.request<OrderResult>(
      `/api/books/${bookId}/order`,
      {
        method: "POST",
        body: JSON.stringify({ shipping }),
      },
      true
    );
  }

  async getOrders() {
    return this.request<OrderListItem[]>("/api/orders", {}, true);
  }

  async getOrder(orderId: number) {
    return this.request<OrderDetailResult>(`/api/orders/${orderId}`, {}, true);
  }

  async cancelOrder(orderId: number) {
    return this.request<{ message: string }>(
      `/api/orders/${orderId}/cancel`,
      { method: "POST" },
      true
    );
  }

  isLoggedIn(): boolean {
    return !!this.getAccessToken();
  }
}

export interface VoucherItem {
  id: number;
  voucher_type: string;
  price: number;
  status: string;
  book_id: number | null;
  purchased_at: string;
  used_at: string | null;
}

export interface BookItem {
  id: number;
  voucher_id: number | null;
  child_name: string;
  child_birth_date: string | null;
  photo_id: number | null;
  job_category: string | null;
  job_name: string | null;
  story_style: string | null;
  art_style: string | null;
  page_count: number;
  book_spec_uid: string;
  plot_input: string | null;
  status: string;
  current_step: number;
  title: string | null;
  story_regen_count: number;
  character_regen_count: number;
  created_at: string;
  updated_at: string;
}

export interface BookListItem {
  id: number;
  child_name: string;
  job_name: string | null;
  status: string;
  current_step: number;
  title: string | null;
  created_at: string;
}

export interface BookUpdateData {
  child_name?: string;
  child_birth_date?: string;
  photo_id?: number;
  job_category?: string;
  job_name?: string;
  story_style?: string;
  art_style?: string;
  page_count?: number;
  book_spec_uid?: string;
  plot_input?: string;
  current_step?: number;
  status?: string;
}

export interface PageImageItem {
  id: number;
  image_path: string;
  generation_index: number;
  is_selected: boolean;
  created_at: string;
}

export interface PageItem {
  id: number;
  book_id: number;
  page_number: number;
  page_type: string;
  scene_description: string | null;
  text_content: string | null;
  image_regen_count: number;
  images: PageImageItem[];
  created_at: string;
  updated_at: string;
}

export interface GenerateResult {
  status: string;
  pages: PageItem[];
}

export interface RegenerateStoryResult {
  status: string;
  story_regen_count: number;
  pages: PageItem[];
}

export interface RegenerateImageResult {
  page_id: number;
  image_regen_count: number;
  images: PageImageItem[];
}

export interface CharacterSheetItem {
  id: number;
  book_id: number;
  image_path: string;
  generation_index: number;
  is_selected: boolean;
  created_at: string;
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

export interface ShippingData {
  recipient_name: string;
  recipient_phone: string;
  postal_code: string;
  address1: string;
  address2?: string;
  shipping_memo?: string;
}

export interface EstimateResult {
  product_amount: number;
  shipping_fee: number;
  packaging_fee: number;
  total_amount: number;
  paid_credit_amount: number;
  credit_balance: number;
  credit_sufficient: boolean;
}

export interface OrderResult {
  id: number;
  book_id: number;
  bookprint_order_uid: string | null;
  status: string;
  status_code: number;
  recipient_name: string;
  recipient_phone: string;
  postal_code: string;
  address1: string;
  address2: string | null;
  shipping_memo: string | null;
  total_amount: number;
  ordered_at: string;
  updated_at: string;
}

export interface OrderListItem {
  id: number;
  book_id: number;
  status: string;
  status_code: number;
  recipient_name: string;
  total_amount: number;
  ordered_at: string;
}

export interface OrderDetailResult {
  id: number;
  book_id: number;
  bookprint_order_uid: string | null;
  status: string;
  status_code: number;
  recipient_name: string;
  recipient_phone: string;
  postal_code: string;
  address1: string;
  address2: string | null;
  shipping_memo: string | null;
  total_amount: number;
  tracking_number: string | null;
  tracking_carrier: string | null;
  ordered_at: string;
  updated_at: string;
}

export const apiClient = new ApiClient();
