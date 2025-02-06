import asyncio
import uuid

from flask import jsonify, request

from probots.db import DB
from probots.models.user import User
from probots.models.mixins.pydantic_base import BaseSchema
from probots.app import APP


class LoginRequest(BaseSchema):
    username: str
    access_code: str


class LoginResponse(BaseSchema):
    status: str
    session_id: str


@APP.route("/api/login", methods=["POST"])
def login():
    login_request = LoginRequest(**request.get_json())

    user = User.with_name(login_request.username)

    if user:
        if user.access_code == login_request.access_code:
            user.session_id = str(uuid.uuid4())
            DB.session.commit()

            return LoginResponse(
                status="success", session_id=user.session_id
            ).model_dump_json(), 200
        else:
            return jsonify({"message": "Unauthorized"}), 401
    else:
        user = User(
            name=login_request.username,
            access_code=login_request.access_code,
            session_id=str(uuid.uuid4()),
        )
        DB.session.add(user)
        DB.session.commit()

        return LoginResponse(
            status="success", session_id=user.session_id
        ).model_dump_json(), 201
