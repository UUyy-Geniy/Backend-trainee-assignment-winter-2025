from fastapi import APIRouter, Depends, Path, status
from typing import Annotated

from api.deps import get_current_user, get_user_service
from models import User
from services.user import UserService
from schemas.user import UserInfoResponse, SendCoinRequest, SendCoinResponse, BuyItemResponse
from schemas.auth import AuthRequest, AuthResponse

router = APIRouter()

@router.post("/auth", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def auth(
    auth_request: AuthRequest,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.authenticate_user(auth_request.username, auth_request.password)

@router.get("/info", status_code=status.HTTP_200_OK, response_model=UserInfoResponse)
async def get_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_user_info(current_user.id)

@router.post("/sendCoin", status_code=status.HTTP_200_OK, response_model=SendCoinResponse)
async def send_coins(
    SendCoinRequest: SendCoinRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.send_coins(
        current_user.id,
        SendCoinRequest.toUser,
        SendCoinRequest.amount
)
@router.get("/buy/{item}", status_code=status.HTTP_200_OK, response_model=BuyItemResponse)
async def buy_item(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: UserService = Depends(get_user_service),
    item: str = Path(..., description="Название товара из мерча"),
):
    return await user_service.buy_item(current_user.id, item)
