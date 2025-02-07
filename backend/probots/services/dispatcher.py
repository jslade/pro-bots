from probots.models.session import Session, WebSocket


class Dispatcher:
    def add_session(self, session: Session, ws: WebSocket) -> None:
        pass


DISPATCHER = Dispatcher()
