import threading
import random
import time
from game_core.game_state import GameState
import game_other.audio
import pygame

class GamePlayEvent:
    def trigger(self):
        pass

class InternetOutage(GamePlayEvent):
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

class NasCrashed(GamePlayEvent):
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

class JobArrived(GamePlayEvent):
    def __init__(self):
        self._last_jobs_finished = None

    def trigger(self):
        state = GameState()
        # Only allow new job if previous job is fully completed
        if getattr(state, 'total_shots_finished', 0) != getattr(state, 'total_shots_unfinished', 0):
            return False
        import random
        n = random.randint(2, 4)
        state.total_shots_unfinished = n
        state.job_id += 1  # Mark a new job event (renamed from job_arrived_id)
        state.render_progress_current = 0  # Reset render progress for new job
        state.render_progress_goal = n * 100  # Set goal to total shots * 100
        # You can add a sound or alert here if desired
        return True

    def notify_jobs_finished(self, jobs_finished):
        if self._last_jobs_finished is None:
            self._last_jobs_finished = jobs_finished
        elif jobs_finished != self._last_jobs_finished:
            self._last_jobs_finished = jobs_finished
            self.trigger()

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

RANDOM_GAMEPLAY_EVENTS = [
    InternetOutage(),
    # NasCrashed(),
    # Add more random situation instances here...
]

DETERMINISTIC_GAMEPLAY_EVENTS = [
    JobArrived(),
    # Add more deterministic situation instances here...
]

GAMEPLAY_EVENTS = RANDOM_GAMEPLAY_EVENTS + DETERMINISTIC_GAMEPLAY_EVENTS

START_DELAY = 10  # seconds before situation manager starts

# Start random events in a background thread

def start_random_gameplay_events():
    def random_event_loop():
        time.sleep(START_DELAY)
        while True:
            situation = random.choice(RANDOM_GAMEPLAY_EVENTS)
            situation.trigger()
            time.sleep(random.uniform(10, 30))
    thread = threading.Thread(target=random_event_loop, daemon=True)
    thread.start()

# Deterministic events are checked every second in the main/game loop or a separate thread

def start_deterministic_gameplay_events():
    def deterministic_event_loop():
        while True:
            for event in DETERMINISTIC_GAMEPLAY_EVENTS:
                event.trigger()
            time.sleep(1)  # Tick every second
    thread = threading.Thread(target=deterministic_event_loop, daemon=True)
    thread.start()

power_outage = PowerOutage()
