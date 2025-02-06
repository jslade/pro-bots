from typing import Optional
import structlog
import uuid

from probots.db import DB
from probots.models.user import User
from probots.models.mixins.pydantic_base import BaseSchema

LOGGER = structlog.get_logger(__name__)


class LoginRequest(BaseSchema):
    username: str
    access_code: str


class LoginResult(BaseSchema):
    success: bool
    session_id: Optional[str] = None
    unauthorized: bool = False


class LoginResponse(BaseSchema):
    status: str
    session_id: Optional[str]


class LoginService:
    def login(self, request: LoginRequest) -> LoginResult:
        user = User.with_name(request.username)

        if user:
            if user.access_code == request.access_code:
                user.session_id = str(uuid.uuid4())
                DB.session.commit()

                return LoginResult(success=True, session_id=user.session_id)
            else:
                return LoginResult(success=False, unauthorized=True)
        else:
            user = User(
                name=request.username,
                access_code=request.access_code,
                session_id=str(uuid.uuid4()),
            )
            DB.session.add(user)
            DB.session.commit()

            return LoginResult(success=True, session_id=user.session_id)
