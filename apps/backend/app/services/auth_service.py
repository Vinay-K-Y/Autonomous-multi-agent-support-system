from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories import UserRepository
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.schemas.auth import UserCreate, UserResponse, Token


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, user_data: UserCreate) -> UserResponse:
        # Check if user already exists
        existing_user = await UserRepository.get_by_email(db, user_data.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user = await UserRepository.create(
            db,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at.isoformat(),
        )

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> Token:
        user = await UserRepository.get_by_email(db, email)
        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is inactive")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires,
        )

        return Token(access_token=access_token, token_type="bearer")
