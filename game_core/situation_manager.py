import threading
import random
import time
from game_core.game_state import GameState
import game_other.audio
import pygame

class BaseSituation:
    def trigger(self):
        pass

class InternetOutage(BaseSituation):
    RESTORE_DELAY = 10  # seconds
    WIFI_RESTORE_DELAY = 2  # seconds

    def __init__(self):
        self._restoring = False

    def trigger(self):
        state = GameState()
        if state.is_internet_online == 1 and not self._restoring:
            state.is_internet_online = 0
            state.is_wifi_online = 0
            self._restoring = True
            game_other.audio.play_system_out_sound()
            threading.Timer(self.RESTORE_DELAY, self.restore_internet).start()
            return True
        return False

    def restore_internet(self):
        state = GameState()
        state.is_internet_online = 1
        game_other.audio.play_system_back_sound()
        threading.Timer(self.WIFI_RESTORE_DELAY, self.restore_wifi).start()
        self._restoring = False

    def restore_wifi(self):
        state = GameState()
        state.is_wifi_online = 1

class NasCrashed(BaseSituation):
    RESTORE_DELAY = 10  # seconds
    def __init__(self):
        self._crashed = False

    def trigger(self):
        state = GameState()
        if state.is_nas_online == 1 and not self._crashed:
            state.is_nas_online = 0
            self._crashed = True
            game_other.audio.play_system_out_sound()
            threading.Timer(self.RESTORE_DELAY, self.restore_nas).start()
            return True
        return False

    def restore_nas(self):
        state = GameState()
        state.is_nas_online = 1
        game_other.audio.play_system_back_sound()
        self._crashed = False

class JobArrived(BaseSituation):
    def trigger(self):
        state = GameState()
        import random
        n = random.randint(5, 15)
        state.total_shot_count = n
        state.job_id += 1  # Mark a new job event (renamed from job_arrived_id)
        # You can add a sound or alert here if desired
        return True

class PowerOutage:
    def __init__(self):
        self.active = False

    def trigger(self):
        state = GameState()
        if state.total_power_drain > state.total_breaker_strength:
            if not self.active:
                self.active = True
                game_other.audio.play_power_outage_sound()
        else:
            if self.active:
                self.active = False
                game_other.audio.play_power_up_sound()

    def draw_overlay(self, surface):
        if self.active:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))  # 50% black
            surface.blit(overlay, (0, 0))

SITUATIONS = [
    InternetOutage(),
    NasCrashed(),
    JobArrived(),
    # Add more situation instances here...
]

START_DELAY = 10  # seconds before situation manager starts

def start_situation_manager():
    def situation_loop():
        time.sleep(START_DELAY)  # Wait before starting situations
        while True:
            situation = random.choice(SITUATIONS)
            situation.trigger()
            time.sleep(random.uniform(5, 10))
    thread = threading.Thread(target=situation_loop, daemon=True)
    thread.start()

power_outage = PowerOutage()
