"""인증 서비스 — JWT 토큰 생성/검증, 비밀번호 해싱"""
import re
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 이메일 정규식 (기본적인 검증)
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """토큰 디코딩. 실패 시 None 반환."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def validate_email(email: str) -> bool:
    """이메일 형식 검증"""
    if not email or not EMAIL_REGEX.match(email):
        return False
    return True


def validate_password(password: str) -> bool:
    """비밀번호 길이 검증 (최소 8자)"""
    return len(password) >= 8


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def validate_phone(phone: str) -> bool:
    """전화번호 형식 검증 (한국 휴대폰)"""
    import re
    # 010-1234-5678, 01012345678, 010 1234 5678 등 허용
    cleaned = re.sub(r"[\s\-]", "", phone)
    return bool(re.match(r"^01[016789]\d{7,8}$", cleaned))


def validate_name(name: str) -> bool:
    """이름 검증 (1~50자)"""
    return 1 <= len(name.strip()) <= 50


def create_user(db: Session, email: str, password: str, name: str, phone: str) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name.strip(),
        phone=phone.strip(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
