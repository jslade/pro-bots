from flask import jsonify, request

from probots.app import APP
from probots.services.login_service import LoginRequest, LoginResponse, LoginService


@APP.route("/api/login", methods=["POST"])
def login():
    login_request = LoginRequest(**request.get_json())

    service = LoginService()
    result = service.login(login_request)

    if result.success:
        return LoginResponse(
            status="success", session_id=result.session_id
        ).as_response(), 200
    elif result.unauthorized:
        return jsonify({"message": "Unauthorized"}), 401

    raise Exception("Unexpected error")
