import structlog

from flask import Flask
from flask_sock import Sock

APP = Flask(__name__)

APP.config["DEBUG"] = True
APP.config["SECRET_KEY"] = "secret!"

SOCK = Sock(APP)

LOGGER = structlog.get_logger(__name__)


@SOCK.route("/")
def handle_ws(ws):
    LOGGER.info("Websocket connection established")
    while True:
        data = ws.receive()
        ws.send(data)
