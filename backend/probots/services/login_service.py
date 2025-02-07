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


class ConnectRequest(BaseSchema):
    username: str
    session_id: str


class ConnectResponse(BaseSchema):
    success: bool
    username: Optional[str]


class LoginService:
    def login(self, request: LoginRequest) -> LoginResult:
        user = User.with_name(request.username)

        if user:
            if user.access_code == request.access_code:
                user.session_id = self.generate_user_session_id()
                DB.session.commit()

                return LoginResult(success=True, session_id=user.session_id)
            else:
                return LoginResult(success=False, unauthorized=True)
        else:
            user = User(
                name=request.username,
                access_code=request.access_code,
                session_id=self.generate_user_session_id(),
            )
            DB.session.add(user)
            DB.session.commit()

            return LoginResult(success=True, session_id=user.session_id)

    def connect(self, request: ConnectRequest) -> Optional[User]:
        user = User.with_name(request.username)

        if user and user.session_id == request.session_id:
            LOGGER.info("User connected", user=user.name, session_id=request.session_id)
            return user
        else:
            LOGGER.info(
                "Invalid connection attempt",
                user=request.username,
                session_id=request.session_id,
            )
            return None

    def generate_user_session_id(self) -> str:
        return "user-" + str(uuid.uuid4())[0:8]
