
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserRole
from schemas_auth import (
    UserCreate,
    UserResponse,
    Token,
    ChangePasswordRequest
)
from auth_utils import (
    get_password_hash,
    verify_password,
    create_access_token
)
from dependencies import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_email = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )

    existing_nickname = db.scalar(
        select(User).where(
            User.nickname == user_data.nickname
        )
    )

    if existing_nickname:
        raise HTTPException(
            status_code=400,
            detail="Никнейм уже занят"
        )

    new_user = User(
        nickname=user_data.nickname,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=UserRole.USER.value
    )

    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email или никнейм уже используется"
        )

    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(
            User.email == form_data.username
        )
    )

    if (
        user is None
        or not verify_password(
            form_data.password,
            user.hashed_password
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token({
        "sub": str(user.id)
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.patch("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(
        data.old_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Старый пароль указан неверно"
        )

    if data.old_password == data.new_password:
        raise HTTPException(
            status_code=400,
            detail="Новый пароль должен отличаться от старого"
        )

    current_user.hashed_password = get_password_hash(
        data.new_password
    )

    db.commit()

    return {
        "message": "Пароль успешно изменён"
    }
