from enum import Enum
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ErrorType(str, Enum):
    NOT_FOUND = "not_found"
    VALIDATION = "validation_error"
    BUSINESS = "business_rule_violation"
    AUTH = "authentication_error"
    SYSTEM = "system_error"

class AppException(Exception):
    def __init__(
        self,
        error_type: ErrorType,
        message: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_type = error_type
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        logger.error(f"{error_type}: {message}", extra=details)

class UserAlreadyExistsError(AppException):
    def __init__(self, username: str):
        super().__init__(
            error_type=ErrorType.BUSINESS,
            message="Username already registered",
            status_code=400,
            details={"username": username}
        )

class InsufficientCoinsError(AppException):
    def __init__(self, current_balance: int):
        super().__init__(
            error_type=ErrorType.BUSINESS,
            message="Insufficient coins",
            status_code=400,
            details={"current_balance": current_balance}
        )

class UserNotFoundError(AppException):
    def __init__(self, message: str = "User not found"):
        super().__init__(
            error_type=ErrorType.NOT_FOUND,
            message=message,
            status_code=404,
        )

class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(
            error_type=ErrorType.AUTH,
            message="Invalid credentials",
            status_code=401
        )

class ItemNotFoundError(AppException):
    def __init__(self, item_name: str):
        super().__init__(
            error_type=ErrorType.NOT_FOUND,
            message="Item not found",
            status_code=404,
            details={"item_name": item_name}
        )