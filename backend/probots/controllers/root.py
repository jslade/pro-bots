import asyncio

from ..app import APP


@APP.route("/")
def hello_world():
    return "Hello, World!"
