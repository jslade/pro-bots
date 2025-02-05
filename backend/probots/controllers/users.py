import asyncio

from ..app import APP
from ..models.user import User
from ..utils.validate_pydantic_response import validate_pydantic_response


@APP.route("/user/<username>", methods=["GET"])
def get_user(username: str) -> dict:
    user = User.with_name(username)
    return {"name": user.name}


@APP.route("/user/<username>/program", methods=["GET"])
def get_user_program(username: str) -> dict:
    user = User.with_name(username)
    return {"username": user.name, "program": user.current_program}


@APP.route("/user/<username>/program", methods=["PATCH"])
def update_user_program(username: str) -> dict:
    user = User.with_name(username)
    return {}
