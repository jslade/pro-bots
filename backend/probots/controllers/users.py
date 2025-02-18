import asyncio

from flask import request

from ..app import APP
from ..models.user import User
from ..services.program_service import (
    ProgramService,
    UserProgramUpdateRequest,
    UserProgramUpdateResponse,
)


@APP.route("/user/<username>", methods=["GET"])
def get_user(username: str) -> dict:
    user = User.with_name(username)
    return {"name": user.name}


@APP.route("/user/<username>/program", methods=["GET"])
def get_user_program(username: str) -> dict:
    service = ProgramService()

    user = User.with_name(username)
    if not user:
        raise Exception("User not found")  # TODO: 404 response

    result = service.get_user_program(user)

    return {"username": user.name, "program": result}


@APP.route("/user/<username>/program", methods=["PATCH"])
def update_user_program(username: str) -> dict:
    service = ProgramService()

    user = User.with_name(username)
    if not user:
        raise Exception("User not found")  # TODO: 404 response

    update = UserProgramUpdateRequest(**request.get_json())
    result = service.update_user_program(user, update)

    return UserProgramUpdateResponse(result=result).as_response(), 200
