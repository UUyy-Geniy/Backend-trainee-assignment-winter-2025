from sqlalchemy.orm import selectinload

from exceptions.app_exception import UserNotFoundError, ItemNotFoundError, InsufficientCoinsError, UserAlreadyExistsError, InvalidCredentialsError
from repository.unit_of_work import UnitOfWork
from schemas.auth import AuthResponse
from schemas.user import UserInfoResponse, SendCoinResponse, BuyItemResponse
from schemas.transaction import TransactionInfo, CoinHistoryResponse
from schemas.inventory import InventoryResponse, InventoryItem
from security import verify_password, create_access_token
from models import User, Transaction, MerchItem

class UserService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def authenticate_user(self, username: str, password: str) -> AuthResponse:
        async with self._uow.atomic():
            if user := await self._get_user_by_username(username):
                self._validate_credentials(user, password)
            else:
                user = await self._register_new_user(username, password)
            
            return AuthResponse(
                token=create_access_token({"sub": user.username})
            )

    async def send_coins(self, sender_id: int, receiver_username: str, amount: int) -> SendCoinResponse:
        async with self._uow.atomic():
            sender, receiver = await self._validate_transfer(sender_id, receiver_username, amount)
            
            sender.coins -= amount
            receiver.coins += amount
            
            await self._uow.transactions.create(
                from_user_id=sender.id,
                to_user_id=receiver.id,
                amount=amount
            )
            
            return SendCoinResponse(
                message="Coins sent successfully",
                remaining_coins=sender.coins
            )

    async def buy_item(self, user_id: int, item_name: str) -> BuyItemResponse:
        async with self._uow.atomic():
            user = await self._get_validated_user(user_id)
            item = await self._get_validated_item(item_name)
            
            if user.coins < item.price:
                raise InsufficientCoinsError(current_balance=user.coins)
            
            user.coins -= item.price
            
            await self._update_user_inventory(user.id, item.name)
            
            return BuyItemResponse(
                item=item.name,
                remaining_coins=user.coins
            )

    async def get_user_info(self, user_id: int) -> UserInfoResponse:
        async with self._uow.atomic():
            user = await self._uow.users.get_by_id(
                user_id,
                options=[
                    selectinload(User.purchases),
                    selectinload(User.sent_transactions).joinedload(Transaction.to_user),
                    selectinload(User.received_transactions).joinedload(Transaction.from_user)
                ]
            )
            self._validate_user_exists(user)
            
            return UserInfoResponse(
                coins=user.coins,
                inventory=self._build_inventory_response(user),
                coin_history=await self._build_coin_history(user)
            )

    async def _get_user_by_username(self, username: str) -> User | None:
        return await self._uow.users.get_by_username(username)
        
    async def _is_username_taken(self, username: str) -> bool:
        return await self._uow.users.get_by_username(username) is not None

    async def _register_new_user(self, username: str, password: str) -> User:
        if await self._is_username_taken(username):
            raise UserAlreadyExistsError(username=username)
            
        return await self._uow.users.create(
            username=username,
            password=password,
            coins=1000
        )

    def _validate_credentials(self, user: User, password: str) -> None:
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

    async def _validate_transfer(self, sender_id: int, receiver_username: str, amount: int) -> tuple[User, User]:
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        sender = await self._get_validated_user(sender_id)
        receiver = await self._get_validated_user_by_username(receiver_username)
        
        if sender.id == receiver.id:
            raise ValueError("Cannot transfer coins to yourself")
        
        if sender.coins < amount:
            raise InsufficientCoinsError(current_balance=sender.coins)
            
        return sender, receiver

    async def _get_validated_user(self, user_id: int) -> User:
        if user := await self._uow.users.get_by_id(user_id):
            return user
        raise UserNotFoundError()

    async def _get_validated_user_by_username(self, username: str) -> User:
        if user := await self._uow.users.get_by_username(username):
            return user
        raise UserNotFoundError("Receiver not found")

    async def _get_validated_item(self, item_name: str) -> MerchItem:
        if item := await self._uow.merch.get_by_name(item_name):
            return item
        raise ItemNotFoundError(item_name=item_name)

    async def _update_user_inventory(self, user_id: int, item_name: str) -> None:
        if purchase := await self._uow.purchases.get_by_user_id_and_item_name(user_id=user_id, item_name=item_name):
            purchase.quantity += 1
            await self._uow.purchases.update(purchase)
        else:
            await self._uow.purchases.create(
                user_id=user_id,
                item_name=item_name,
                quantity=1
            )

    def _build_inventory_response(self, user: User) -> InventoryResponse:
        return InventoryResponse(
            inventory=[InventoryItem(type=p.item_name, quantity=p.quantity) 
                  for p in user.purchases]
        )

    async def _build_coin_history(self, user: User) -> CoinHistoryResponse:
        return CoinHistoryResponse(
            received=[await self._build_transaction_info(t, "from") 
                     for t in user.received_transactions],
            sent=[await self._build_transaction_info(t, "to") 
                 for t in user.sent_transactions]
        )

    async def _build_transaction_info(self, transaction: Transaction, direction: str) -> TransactionInfo:
        if direction == "received":
            return TransactionInfo(
                fromUser=transaction.from_user.username,
                toUser=transaction.to_user.username,
                amount=transaction.amount,
                timestamp=transaction.timestamp.isoformat()
            )
        return TransactionInfo(
            fromUser=transaction.from_user.username,
            toUser=transaction.to_user.username,
            amount=transaction.amount,
            timestamp=transaction.timestamp.isoformat()
        )

    def _validate_user_exists(self, user: User | None) -> None:
        if not user:
            raise UserNotFoundError()
