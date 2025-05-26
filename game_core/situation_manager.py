import threading
import random
import time
import game_core.game_state
import game_other.audio

class BaseSituation:
    def maybe_trigger(self):
        pass

class InternetFluctuationSituation(BaseSituation):
    def __init__(self):
        self.cooldown = 0
        self._restoring = False

    def maybe_trigger(self):
        from game_core.game_state import GameState
        state = GameState()
        if state.is_internet_online == 1 and random.random() < 0.2 and not self._restoring:
            state.is_internet_online = 0
            self._restoring = True
            game_other.audio.play_internet_outage_sound()
            threading.Timer(10, self.restore_internet).start()
            return True
        return False

    def restore_internet(self):
        from game_core.game_state import GameState
        state = GameState()
        state.is_internet_online = 1
        self._restoring = False

# Add more situation classes here as needed

SITUATIONS = [
    InternetFluctuationSituation(),
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
