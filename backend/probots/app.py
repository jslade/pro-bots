import structlog

from flask import Flask
from flask_sock import Sock

APP = Flask(__name__)

APP.config["DEBUG"] = True

SOCK = Sock(APP)
