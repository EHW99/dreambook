"""주문 API 라우터"""
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.book import Book
from app.models.order import Order
from app.models.page import Page
from app.models.page_image import PageImage
from app.schemas.order import (
    OrderRequest,
    ShippingUpdateRequest,
    EstimateResponse,
    OrderResponse,
    OrderListResponse,
    OrderDetailResponse,
)
from app.services.bookprint import BookPrintService, BookPrintAPIError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


def _get_book_or_error(db: Session, book_id: int, user: User) -> Book:
    """동화책 조회 + 소유자 확인"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 접근할 수 있습니다",
        )
    return book


def _get_pages_data(db: Session, book: Book) -> list[dict]:
    """동화책의 페이지 데이터 조회 (텍스트 + 선택된 이미지 경로)"""
    pages = db.query(Page).filter(Page.book_id == book.id).order_by(Page.page_number).all()
    pages_data = []
    for page in pages:
        selected_image = None
        for img in page.images:
            if img.is_selected:
                selected_image = img
                break

        image_path = ""
        if selected_image and selected_image.image_path:
            img_path = selected_image.image_path
            if os.path.isabs(img_path) and os.path.exists(img_path):
                # 절대 경로가 이미 실제 파일을 가리킴
                image_path = img_path
            elif img_path.startswith("/"):
                # 서버 로컬 경로 — uploads 디렉토리에서 찾기
                from app.services.photo import UPLOAD_DIR
                local_path = os.path.join(UPLOAD_DIR, os.path.basename(img_path))
                if os.path.exists(local_path):
                    image_path = local_path
            elif os.path.exists(img_path):
                image_path = img_path

        pages_data.append({
            "text": page.text_content or "",
            "image_path": image_path,
            "page_number": page.page_number,
            "page_type": page.page_type,
        })

    return pages_data


@router.post("/books/{book_id}/estimate", response_model=EstimateResponse)
async def get_estimate(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """견적 조회 — Book Print API 연동"""
    book = _get_book_or_error(db, book_id, user)

    # 편집 완료(editing/completed) 상태 확인
    if book.status not in ("editing", "completed"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="편집이 완료된 동화책만 견적을 조회할 수 있습니다",
        )

    service = BookPrintService()
    try:
        # 충전금 확인 + 충전
        await service.ensure_sufficient_credits()

        # 이미 bookprint_book_uid가 있으면 재사용, 없으면 전체 워크플로우 필요
        if book.bookprint_book_uid:
            estimate = await service.get_estimate(book.bookprint_book_uid)
        else:
            # 아직 Book Print에 책이 없으면 임시 생성 -> 견적 조회
            # 실제로는 주문 시 전체 워크플로우를 실행하므로,
            # 여기서는 판형 기반 예상 가격 계산
            estimate = _calculate_local_estimate(book)
    except BookPrintAPIError as e:
        logger.error(f"견적 조회 실패: {e.message}")
        # API 오류 시 로컬 견적 계산으로 대체
        estimate = _calculate_local_estimate(book)
    finally:
        await service.close()

    return EstimateResponse(
        product_amount=estimate.get("productAmount", 0),
        shipping_fee=estimate.get("shippingFee", 3500),
        packaging_fee=estimate.get("packagingFee", 500),
        total_amount=estimate.get("totalAmount", 0),
        paid_credit_amount=estimate.get("paidCreditAmount", 0),
        credit_balance=estimate.get("creditBalance", 0),
        credit_sufficient=estimate.get("creditSufficient", True),
    )


def _calculate_local_estimate(book: Book) -> dict:
    """Book Print API 호출 없이 로컬에서 예상 가격 계산 (Sandbox 테스트 가격)"""
    # Sandbox에서는 테스트 가격 (100원 이하) 적용
    # 하지만 실제 가격 구조를 보여주기 위해 정상 가격 공식 사용
    page_count = book.page_count or 24
    spec_uid = book.book_spec_uid or "SQUAREBOOK_HC"

    # 가격 계산 (테스트용)
    SPEC_PRICES = {
        "SQUAREBOOK_HC": {"base": 19800, "per_increment": 500, "page_min": 24},
        "PHOTOBOOK_A4_SC": {"base": 15800, "per_increment": 400, "page_min": 24},
        "PHOTOBOOK_A5_SC": {"base": 12800, "per_increment": 300, "page_min": 50},
    }

    spec = SPEC_PRICES.get(spec_uid, SPEC_PRICES["SQUAREBOOK_HC"])
    extra_pages = max(0, page_count - spec["page_min"])
    product_amount = spec["base"] + (extra_pages // 2) * spec["per_increment"]
    shipping_fee = 3500
    packaging_fee = 500
    total_amount = product_amount + shipping_fee + packaging_fee
    paid_credit_amount = int(total_amount * 1.1 / 10) * 10  # VAT 포함

    return {
        "productAmount": product_amount,
        "shippingFee": shipping_fee,
        "packagingFee": packaging_fee,
        "totalAmount": total_amount,
        "paidCreditAmount": paid_credit_amount,
        "creditBalance": 0,
        "creditSufficient": True,
    }


@router.post("/books/{book_id}/order", response_model=OrderResponse)
async def create_order(
    book_id: int,
    req: OrderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """주문 생성 — Book Print API 전체 워크플로우 실행"""
    book = _get_book_or_error(db, book_id, user)

    # 상태 확인
    if book.status not in ("editing", "completed"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="편집이 완료된 동화책만 주문할 수 있습니다",
        )

    # 이미 주문이 존재하는지 확인
    existing_order = db.query(Order).filter(Order.book_id == book.id).first()
    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 주문된 동화책입니다",
        )

    # 페이지 데이터 조회
    pages_data = _get_pages_data(db, book)
    if not pages_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="동화책에 페이지가 없습니다",
        )

    # 배송 정보 구성 (Book Print API 형식)
    shipping = {
        "recipientName": req.shipping.recipient_name,
        "recipientPhone": req.shipping.recipient_phone,
        "postalCode": req.shipping.postal_code,
        "address1": req.shipping.address1,
    }
    if req.shipping.address2:
        shipping["address2"] = req.shipping.address2
    if req.shipping.shipping_memo:
        shipping["memo"] = req.shipping.shipping_memo

    # 표지 이미지 (첫 페이지 이미지 사용)
    cover_image_path = None
    if pages_data:
        cover_image_path = pages_data[0].get("image_path") or None

    service = BookPrintService()
    try:
        # 전체 워크플로우 실행
        result = await service.execute_order_workflow(
            title=book.title or f"{book.child_name}의 동화책",
            book_spec_uid=book.book_spec_uid,
            pages_data=pages_data,
            cover_image_path=cover_image_path,
            shipping=shipping,
        )

        # DB에 주문 레코드 생성
        order = Order(
            user_id=user.id,
            book_id=book.id,
            bookprint_order_uid=result.get("order_uid"),
            status="PAID",
            status_code=20,
            recipient_name=req.shipping.recipient_name,
            recipient_phone=req.shipping.recipient_phone,
            postal_code=req.shipping.postal_code,
            address1=req.shipping.address1,
            address2=req.shipping.address2,
            shipping_memo=req.shipping.shipping_memo,
            total_amount=int(result.get("paid_credit_amount", 0)),
        )
        db.add(order)

        # 책 상태 업데이트
        book.status = "completed"
        book.bookprint_book_uid = result.get("book_uid")

        db.commit()
        db.refresh(order)

        return order

    except BookPrintAPIError as e:
        logger.error(f"주문 실패: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"주문 처리 중 오류가 발생했습니다: {e.message}",
        )
    finally:
        await service.close()


@router.get("/orders", response_model=List[OrderListResponse])
def list_orders(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내 주문 목록 조회"""
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.ordered_at.desc()).all()
    result = []
    for order in orders:
        data = OrderListResponse.model_validate(order)
        if order.book:
            data.book_title = order.book.title or f"{order.book.child_name}의 동화책"
        result.append(data)
    return result


@router.get("/orders/{order_id}", response_model=OrderDetailResponse)
def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """주문 상세 조회"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다",
        )
    if order.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 주문만 조회할 수 있습니다",
        )
    return order


@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """주문 취소"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다",
        )
    if order.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 주문만 취소할 수 있습니다",
        )

    # PAID(20) 또는 PDF_READY(25) 상태만 취소 가능
    if order.status_code not in (20, 25):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 상태에서는 주문을 취소할 수 없습니다",
        )

    if order.bookprint_order_uid:
        service = BookPrintService()
        try:
            await service.cancel_order(order.bookprint_order_uid)
        except BookPrintAPIError as e:
            logger.error(f"주문 취소 실패: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"주문 취소 중 오류가 발생했습니다: {e.message}",
            )
        finally:
            await service.close()

    from datetime import datetime, timezone
    order.status = "CANCELLED_REFUND"
    order.status_code = 81
    order.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "주문이 취소되었습니다"}


@router.patch("/orders/{order_id}/shipping", response_model=OrderDetailResponse)
async def update_order_shipping(
    order_id: int,
    req: ShippingUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """배송지 변경 — 변경할 필드만 전달"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다",
        )
    if order.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 주문만 수정할 수 있습니다",
        )

    # PAID(20), PDF_READY(25), CONFIRMED(30) 상태만 변경 가능
    if order.status_code not in (20, 25, 30):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 상태에서는 배송지를 변경할 수 없습니다",
        )

    # 전달된 필드만 추출 (None이 아닌 것들)
    update_fields = req.model_dump(exclude_unset=True)
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="변경할 배송지 정보를 입력해주세요",
        )

    # Book Print API에 변경 전달
    if order.bookprint_order_uid:
        # 필드명 매핑 (snake_case → camelCase)
        field_map = {
            "recipient_name": "recipientName",
            "recipient_phone": "recipientPhone",
            "postal_code": "postalCode",
            "address1": "address1",
            "address2": "address2",
            "shipping_memo": "memo",
        }
        shipping_data = {}
        for field, value in update_fields.items():
            if field in field_map:
                shipping_data[field_map[field]] = value

        service = BookPrintService()
        try:
            await service.update_shipping(order.bookprint_order_uid, shipping_data)
        except BookPrintAPIError as e:
            logger.error(f"배송지 변경 실패: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"배송지 변경 중 오류가 발생했습니다: {e.message}",
            )
        finally:
            await service.close()

    # DB 업데이트 — 전달된 필드만 변경
    from datetime import datetime, timezone
    for field, value in update_fields.items():
        setattr(order, field, value)
    order.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(order)

    return order
