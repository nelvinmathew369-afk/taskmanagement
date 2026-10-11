from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserLogin, UserRegister, UserResponse, TokenResponse
from app import crud, auth

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticate user by username and password, returning JWT access token."
)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db=db, username=payload.username)
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token(data={"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
def register(
    payload: UserRegister,
    db: Session = Depends(get_db)
):
    if crud.get_user_by_username(db=db, username=payload.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken."
        )
    if crud.get_user_by_email(db=db, email=payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    hashed_pw = auth.hash_password(payload.password)
    user = crud.create_user(db=db, user_in=payload, password_hash=hashed_pw)
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user details"
)
def get_me(
    current_user = Depends(auth.get_current_user)
):
    return current_user
