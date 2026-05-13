import asyncio
from pathlib import Path
from uuid import uuid4
from fastapi import WebSocket, WebSocketDisconnect

from game_core.config import level_dir
from Backend.session_controller.SessionManager import SessionManager

session_manager = SessionManager()


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(uuid4())
    session = session_manager.get_session(client_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "get_maps":
                result = [file.stem for file in Path(level_dir).glob('*.pml')]
                await websocket.send_json({"action": "get_maps", "maps": result})

            if action == "load_map":
                result = session.handle_load_maps(data.get("map_name"))
                await websocket.send_json(result)

            elif action == "start":
                error = session.handle_start()
                if error:
                    await websocket.send_json(error)
                else:
                    if session.game_task_send is None or session.game_task_send.done():
                        session.game_task_send = asyncio.create_task(session.game_loop_send(websocket))
                    else:
                        await websocket.send_json({"action": "stop", "message": "WebSocket Sendetask läuft bereits"})

            elif action == "stop":
                await websocket.send_json(session.handle_stop())
                await websocket.send_json({"action": "stop", "message": "ready"})

            elif action == "pause":
                session.is_game_paused = True
                await websocket.send_json({"action": "pause", "message": "The game is paused."})

            elif action == "continue":
                session.is_game_paused = False
                await websocket.send_json({"action": "continue", "message": "The game is not paused anymore"})

            elif data.get("action") == "step":
                await websocket.send_json(session.handle_step())

            elif data.get("action") == "change_speed":
                error = session.handle_change_speed(data)
                if error:
                    await websocket.send_json(error)

            elif data.get("action") == "get_seed":
                await websocket.send_json(session.handle_get_seed())

            elif data.get("action") == "set_seed":
                error = session.handle_set_seed(data)
                if error:
                    await websocket.send_json(error)

            elif data.get("action") == "multiple_runs":
                number_of_runs = data.get("number_of_runs")
                for result in session.handle_multiple_runs(number_of_runs):
                    await websocket.send_json(result)

    except WebSocketDisconnect:
        session_manager.remove_session(client_id)
    finally:
        session_manager.remove_session(client_id)
        print(f"Session für {client_id} entfernt")