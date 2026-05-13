from fastapi import WebSocket
from Backend.session_controller.GameSession import GameSession


class SessionManager:
    def __init__(self):
        self.sessions: dict[str, GameSession] = {}

    def get_session(self, client_id: str, websocket: WebSocket = None) -> GameSession:
        if client_id not in self.sessions and websocket:
            self.sessions[client_id] = GameSession(websocket)
        return self.sessions[client_id]

    def remove_session(self, client_id: str):
        if client_id in self.sessions:
            del self.sessions[client_id]
