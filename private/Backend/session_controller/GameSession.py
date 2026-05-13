import asyncio
import ctypes
import importlib
import os
import pkgutil
import random
import sys
import threading
import time
import traceback

import numpy as np
from starlette.websockets import WebSocket
from game_core.config import default_game_speed, level_dir
import Backend.PacmanAgent as pacman_module
from Backend.PacmanAgent import PacmanAgent


class GameSession:
    def __init__(self, websocket: WebSocket = None):
        self.agent = PacmanAgent()
        self.steps: list = []
        self.seed: int = 0
        self.thread_running = False
        self.game_speed = default_game_speed
        self.game_task_send = None
        self.current_level_in_pml = None
        self.is_game_paused = False
        self.step_thread = None
        self.thread_stop_event = threading.Event()
        self.websocket: WebSocket = websocket

    def game_over(self):
        return self.agent.terminated or self.agent.truncated

    async def game_loop_send(self, websocket: WebSocket):
        while self.agent.is_running:
            if self.is_game_paused:
                await asyncio.sleep(default_game_speed)
                continue
            try:
                data = self.next_step()
            except Exception as e:
                print(f"Error Next step: {e}")
                sys.stdout.flush()
            await websocket.send_json(data)

            await asyncio.sleep(self.game_speed)

    def run_step_thread(self):
        """Thread-Funktion, die kontinuierlich `step()` aufruft"""
        result = None
        while self.thread_running:
            if self.game_over():
                self.thread_running = False
            try:
                result = self.agent.step()
            except IndexError:
                print("IndexError in step() – möglicherweise Zugriff auf leere Liste?")
                print(traceback.format_exc())
                self.thread_running = False

            except AttributeError:
                print(
                    "AttributeError in step() – möglicherweise fehlt ein Attribut oder Methode?"
                )
                print(traceback.format_exc())
                self.thread_running = False

            except TypeError:
                print("TypeError in step() – möglicherweise falscher Datentyp?")
                print(traceback.format_exc())
                self.thread_running = False

            except ValueError:
                print(
                    "ValueError in step() – möglicherweise ungültiger Wert übergeben?"
                )
                print(traceback.format_exc())
                self.thread_running = False

            except Exception as e:
                print(f"Unbekannter Fehler in step(): {e}")
                print(traceback.format_exc())
                self.thread_running = False

            if result:
                current_view, is_last_step, statistics = result
                self.steps.append((current_view, is_last_step, statistics))
            else:
                self.thread_running = False

    def restore_state(self):
        self.thread_stop_event.set()
        for t in threading.enumerate():
            if t.name == "StepThread":
                t.join(timeout=2)
                if t.is_alive():
                    kill_thread(t)

        self.thread_stop_event.clear()
        self.step_thread = None
        self.thread_running = False

        self.game_task_send = None
        self.is_game_paused = False
        self.steps.clear()
        # This can set the agent to None
        self.agent = reload_agent()

        if not self.agent:
            print("Error: reload_files()")
            return None

        obs, info = self.agent.reset(self.seed, self.current_level_in_pml)
        return obs.tolist()

    def next_step(self):
        if len(self.steps) > 0:
            obs, is_last_step, statistics = self.steps.pop(0)  # info contains only the view, or all statistics
            if is_last_step:
                data = {
                    "action": "game_over",
                    "view": obs.tolist(),
                    "turns": int(statistics["turns"]),
                    "remainingdots": int(statistics["remainingdots"]),
                    "collecteddots": int(statistics["collecteddots"]),
                }
                return data
            else:  # is not last frame
                data = {"action": "step", "view": obs.tolist()}
                return data

        elif len(self.steps) == 0 and not self.game_over():
            data = {
                "action": "error_code",
                "message": "The game is still being computed. Please wait...",
            }
            return data

        else:
            self.restore_state()
            print("Pac terminated!")
            data = {"action": "stop", "message": "ready"}
            return data

    def start_thread(self):
        if not any(t.name == "StepThread" for t in threading.enumerate()):
            self.thread_running = True
            self.step_thread = threading.Thread(
                target=self.run_step_thread, name="StepThread", daemon=False
            )
            self.step_thread.start()
            print("Pac ist gestartet")
            sys.stdout.flush()
        else:
            print("could not start Pac")
            return {
                "action": "error_code",
                "message": "Problems with starting the thread",
            }

    def validate_game_start_conditions(self):
        if self.agent.env.view is None:
            return {"action": "error_code", "message": "view is None"}
        elif (
            isinstance(self.agent.env.view, np.ndarray) and self.agent.env.view.size == 0
        ):
            return {"action": "error_code", "message": "no level is set"}
        elif self.agent.is_running:
            return {"action": "error_code", "message": "A game is already running"}
        else:
            self.agent.is_running = True

    def handle_start(self):
        self.restore_state()
        possible_error = self.validate_game_start_conditions()
        if possible_error:
            return possible_error

        elif not possible_error:
            thread_error = self.start_thread()
            if thread_error:
                return thread_error

    def handle_stop(self):
        view_json = self.restore_state()
        if self.agent is not None:
            self.agent.is_running = False
        sys.stdout.flush()
        if not view_json:
            data = {
                "action": "error_code",
                "message": "View is None, Error reload_state().",
            }
            return data
        else:
            data = {"action": "load_map", "view": view_json}
            return data

    def handle_load_maps(self, map_name_raw: str):
        if self.agent.is_running:
            view_json = self.restore_state()
            if not view_json:
                return {
                    "action": "error_code",
                    "message": " View is None, Error restore_state().",
                }

        if not isinstance(map_name_raw, str):
            return {
                "action": "error_code",
                "message": f"The provided 'map_name' ({map_name_raw}) must be a string.",
            }

        map_name = map_name_raw + ".pml"

        try:
            obs, info = self.agent.env.reset(
                seed=self.seed, level=os.path.join(level_dir, map_name)
            )
        except Exception as e:
            return {"action": "error_code", "message": f"Error A is: {str(e)}"}
        try:
            view_json = obs.tolist()
        except Exception as e:
            return {
                "action": "error_code",
                "message": f"Error B is: {str(e)} with info: {obs}",
            }

        self.current_level_in_pml = os.path.join(level_dir, map_name)

        if view_json:
            return {"action": "load_map", "view": view_json}
        else:
            return {"action": "error_code", "message": "view is None"}

    def handle_step(self):
        if self.is_game_paused:
            return self.next_step()
        else:
            return {"action": "error_code", "message": "The game is not paused."}

    def handle_change_speed(self, data):
        if isinstance(data.get("speed"), (int, float)):
            self.game_speed = data.get("speed")
        else:
            return {"action": "error_code", "message": "invalid speed"}

    def handle_multiple_runs(self, data):
        self.restore_state()
        number_of_runs = data
        error = check_number_of_runs(number_of_runs)
        if error:
            yield error

        games_done = 0
        games_won: int = 0
        sum_dots_left: int = 0

        while games_done < number_of_runs:
            self.restore_state()
            result = self.run_single_game(games_done)
            if result.get("action") == "error_code":
                yield result
                continue

            sum_dots_left, games_won = update_multiple_runs_stats(
                result, sum_dots_left, games_won
            )
            games_done += 1
            yield result

        yield get_end_statistics(games_won, number_of_runs, sum_dots_left)

    def run_single_game(self, games_done: int):
        error = self.validate_game_start_conditions()
        if error:
            return error

        error = self.start_thread()
        if error:
            return error

        while self.thread_running:  # TODO schönere Lösung finden
            time.sleep(0.001)

        current_view, is_last_step, info = self.steps.pop()  # get last element
        if not is_last_step:
            return {
                "action": "error_code",
                "message": "No more steps, but game is not over",
            }

        data = {
            "action": "single_game_over_multiple_runs",
            "turns": int(info["turns"]),
            "remainingdots": int(info["remainingdots"]),
            "collecteddots": int(info["collecteddots"]),
            "number_of_games_done": games_done,
        }

        self.restore_state()
        return data

    def handle_get_seed(self):
        if self.current_level_in_pml is None:
            return {"action": "error_code", "message": "No level is set -> no seed"}
        else:
            return {"action": "get_seed", "seed": self.agent.env.seed}

    def handle_set_seed(self, data):
        if isinstance(data.get("seed"), int):
            seed_value = data.get("seed")
            if seed_value == 0:
                self.seed = random.randint(1, 2**32 - 1)
            else:
                self.seed = data.get("seed")
        else:
            return {"action": "error_code", "message": "Seed is not an int"}


def reload_agent():
    try:
        reload_backend()
        importlib.reload(pacman_module)
        # reload_all_packages_in_dir(".")

        return pacman_module.PacmanAgent()
    except Exception as e:
        print(f"Fehler beim Reload von PacmanAgent: {e}")
        sys.stdout.flush()
        return None


def reload_backend():
    importlib.invalidate_caches()

    module_names = [
        name for name in sys.modules if name == "Backend" or name.startswith("Backend.")
    ]

    # erst tiefere Module, dann übergeordnete
    module_names.sort(key=lambda x: x.count("."), reverse=True)

    for name in module_names:
        try:
            importlib.reload(sys.modules[name])
            print(f"Reloaded: {name}")
        except Exception as e:
            print(f"Fehler beim Reload von {name}: {e}")


def reload_modules(package_name):
    if package_name not in sys.modules:
        return

    package = sys.modules[package_name]

    # load submodules first because of cache
    submodules = []
    for _, module_name, _ in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        if module_name in sys.modules:
            submodules.append(module_name)

    for module_name in submodules:
        importlib.reload(sys.modules[module_name])

    # then load main-module
    importlib.reload(package)


def reload_all_packages_in_dir(directory):
    for name in os.listdir(directory):
        full_path = os.path.join(directory, name)
        if os.path.isdir(full_path) and os.path.isfile(
            os.path.join(full_path, "__init__.py")
        ):
            if name in sys.modules:
                reload_modules(name)
            else:
                try:
                    importlib.import_module(name)
                    reload_modules(name)
                except Exception as e:
                    print(f"Fehler beim Reload von PacmanAgent: {e}")


def kill_thread(thread):
    """Erzwingt das Beenden eines Threads"""
    if not thread.is_alive():
        return
    print("Erzwinge das Beenden von StepThread!")
    sys.stdout.flush()
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), ctypes.py_object(SystemExit)
    )
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, 0)
        print("Fehler beim erzwungenen Stop des Threads!")
        sys.stdout.flush()


def check_number_of_runs(number_of_runs: int):
    if not isinstance(number_of_runs, int):
        return {"action": "error_code", "message": "number_of_runs must be an integer"}
    elif number_of_runs < 1:
        return {"action": "error_code", "message": "Number of runs is lower than 1"}


def update_multiple_runs_stats(result, sum_dots_left: int, games_won: int):
    remaining_dots = result["remainingdots"]
    sum_dots_left += remaining_dots
    if remaining_dots == 0:
        games_won += 1
    return sum_dots_left, games_won


def get_end_statistics(games_won: int, number_of_runs: int, sum_dots_left: int):
    games_won_in_percent: float = games_won / number_of_runs * 100
    games_won_in_percent: str = str(games_won_in_percent) + "%"
    average_dots_left: int = sum_dots_left // number_of_runs

    return {
        "action": "multiple_runs_done",
        "games_won": games_won_in_percent,
        "average_dots_left": int(average_dots_left),
    }
