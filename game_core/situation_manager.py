import threading
import random
import time
from game_core.game_state import GameState
import game_other.audio

class BaseSituation:
    def maybe_trigger(self):
        pass

class InternetOutage(BaseSituation):
    RESTORE_DELAY = 10  # seconds
    WIFI_RESTORE_DELAY = 2  # seconds

    def __init__(self):
        self._restoring = False

    def maybe_trigger(self):
        state = GameState()
        if state.is_internet_online == 1 and random.random() < 0.2 and not self._restoring:
            state.is_internet_online = 0
            state.is_wifi_online = 0
            self._restoring = True
            game_other.audio.play_internet_outage_sound()
            threading.Timer(self.RESTORE_DELAY, self.restore_internet).start()
            return True
        return False

    def restore_internet(self):
        state = GameState()
        state.is_internet_online = 1
        game_other.audio.play_internet_reconnect_sound()
        threading.Timer(self.WIFI_RESTORE_DELAY, self.restore_wifi).start()
        self._restoring = False

    def restore_wifi(self):
        state = GameState()
        state.is_wifi_online = 1

SITUATIONS = [
    InternetOutage(),
    # Add more situation instances here...
]

def start_situation_manager():
    def situation_loop():
        while True:
            for situation in SITUATIONS:
                situation.maybe_trigger()
            time.sleep(1)
    thread = threading.Thread(target=situation_loop, daemon=True)
    thread.start()
