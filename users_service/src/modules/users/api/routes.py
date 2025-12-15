from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from core import get_db, get_current_user
from ..commands import RegisterUserCommand, UpdateUserCommand, LoginCommand
from ..queries import GetUserByIdQuery
from ..handlers import (
    RegisterUserHandler,
    UpdateUserHandler,
    LoginHandler,
    GetUserByIdHandler,
)
from ..repositories.impl import SqlAlchemyUserWriteRepository, SqlAlchemyUserReadRepository
from ..exceptions import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
    InvalidCredentialsException,
)
from ..dto import UserDTO

router = APIRouter()


@router.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    repository = SqlAlchemyUserWriteRepository(db)
    handler = RegisterUserHandler(repository)

    command = RegisterUserCommand(
        email=user.email,
        username=user.username,
        password=user.password,
        bio=user.bio,
        image_url=user.image_url,
    )

    try:
        user_id = await handler.handle(command)
    except EmailAlreadyExistsException:
        raise HTTPException(status_code=400, detail="Email already registered")
    except UsernameAlreadyExistsException:
        raise HTTPException(status_code=400, detail="Username already taken")

    read_repo = SqlAlchemyUserReadRepository(db)
    created_user = await read_repo.find_by_id(user_id)
    return _dto_to_response(created_user)


@router.post("/users/login", response_model=schemas.Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    repository = SqlAlchemyUserReadRepository(db)
    handler = LoginHandler(repository)

    command = LoginCommand(
        username=form_data.username,
        password=form_data.password,
    )

    try:
        access_token, token_type = await handler.handle(command)
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": access_token, "token_type": token_type}


@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    repository = SqlAlchemyUserReadRepository(db)
    handler = GetUserByIdHandler(repository)
    
    query = GetUserByIdQuery(user_id=user_id)
    user = await handler.handle(query)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return _dto_to_response(user)


@router.get("/user", response_model=schemas.UserResponse)
async def read_current_user(
    current_user: UserDTO = Depends(get_current_user),
):
    return _dto_to_response(current_user)


@router.put("/user", response_model=schemas.UserResponse)
async def update_current_user(
    user_in: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserDTO = Depends(get_current_user),
):
    repository = SqlAlchemyUserWriteRepository(db)
    handler = UpdateUserHandler(repository)

    command = UpdateUserCommand(
        user_id=current_user.id,
        email=user_in.email,
        username=user_in.username,
        password=user_in.password,
        bio=user_in.bio,
        image_url=user_in.image_url,
    )

    try:
        await handler.handle(command)
    except EmailAlreadyExistsException:
        raise HTTPException(status_code=400, detail="Email already registered")
    except UsernameAlreadyExistsException:
        raise HTTPException(status_code=400, detail="Username already taken")

    read_repo = SqlAlchemyUserReadRepository(db)
    updated_user = await read_repo.find_by_id(current_user.id)
    return _dto_to_response(updated_user)


def _dto_to_response(dto: UserDTO) -> dict:
    return {
        "id": dto.id,
        "email": dto.email,
        "username": dto.username,
        "bio": dto.bio,
        "image_url": dto.image_url,
    }
