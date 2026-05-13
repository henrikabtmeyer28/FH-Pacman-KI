from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from Backend.session_controller.websocket_handler import websocket_endpoint

fastapi = FastAPI()

fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hier wird dein WebSocket-Endpunkt registriert
fastapi.add_api_websocket_route("/ws", websocket_endpoint)