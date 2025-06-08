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

class JobFinished:
    def __init__(self):
        self._last_project_finished = False

    def trigger(self):
        state = GameState()
        if state.total_shots_goal > 0 and state.total_shots_finished == state.total_shots_goal:
            if not self._last_project_finished:
                game_other.audio.play_project_finished_sound()
                state.current_job_finished = 1
                # Add job_budget to total_money when job is finished
                state.total_money += state.job_budget
                self._last_project_finished = True
        else:
            self._last_project_finished = False

class JobArrived(GamePlayEvent):
    def __init__(self):
        self._last_jobs_finished = None
        self._n = 2  # Start at 2

    def trigger(self):
        state = GameState()
        # Only allow new job if previous job is fully completed and current_job_finished is 1
        if getattr(state, 'total_shots_finished', 0) != getattr(state, 'total_shots_goal', 0):
            return False
        if getattr(state, 'current_job_finished', 0) != 1:
            return False
        n = self._n
        # Reset render_progress_allowed to 0 when job is finished
        state.render_progress_allowed = 0
        self._n += 1  # Increment for next job
        state.total_shots_goal = n
        state.job_id += 1
        state.artist_progress_current = 0
        state.artist_progress_goal = n * state.artist_progress_required_per_shot
        state.render_progress_current = 0
        state.render_progress_goal = n * state.render_progress_required_per_shot
        state.job_budget = 10000 * n
        state.current_job_finished = 0  # Reset for next job
        game_other.audio.play_job_arrived_sound()
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
            width, height = surface.get_size()
            # Define cutout using independent start/end percentages
            x_start_pct = 0.5   # 50% of width
            x_end_pct = 0.615     # 60% of width
            y_start_pct = 0.027   # 10% of height
            y_end_pct = 0.12     # 50% of height
            cutout_rect = pygame.Rect(
                int(width * x_start_pct),
                int(height * y_start_pct),
                int(width * (x_end_pct - x_start_pct)),
                int(height * (y_end_pct - y_start_pct))
            )
            # Draw a fully transparent rectangle (cutout)
            pygame.draw.rect(overlay, (0, 0, 0, 0), cutout_rect)
            surface.blit(overlay, (0, 0))

class ClimateControl:
    def __init__(self, interval=10, start_temp=None):
        self.interval = interval  # seconds
        self._running = False
        self._thread = None
        self._direction = 1  # 1 for up, -1 for down
        self._target = None
        self._min_up = 23
        self._max_up = 25
        self._min_down = 18
        self._max_down = 20
        if start_temp is None:
            self._start_temp = GameState().temperature
        else:
            self._start_temp = start_temp

    def start(self):
        # Disabled for now: do not start the background thread
        # if not self._running:
        #     self._running = True
        #     import threading
        #     self._thread = threading.Thread(target=self._run, daemon=True)
        #     self._thread.start()
        pass

    def stop(self):
        self._running = False

    def _pick_new_target(self, current_temp):
        import random
        if self._direction == 1:
            self._target = random.randint(self._min_up, self._max_up)
        else:
            self._target = random.randint(self._min_down, self._max_down)

    def _run(self):
        import time
        from game_core.game_state import GameState
        state = GameState()
        state.temperature = self._start_temp
        self._pick_new_target(state.temperature)
        while self._running:
            time.sleep(self.interval)
            state = GameState()
            if self._direction == 1:
                if state.temperature < self._target:
                    state.temperature += 1
                else:
                    self._direction = -1
                    self._pick_new_target(state.temperature)
            else:
                if state.temperature > self._target:
                    state.temperature -= 1
                else:
                    self._direction = 1
                    self._pick_new_target(state.temperature)

RANDOM_GAMEPLAY_EVENTS = [
    InternetOutage(),
    # NasCrashed(),
    # Add more random situation instances here...
]

DETERMINISTIC_GAMEPLAY_EVENTS = [
    JobArrived(),
    JobFinished(),
    # Add more deterministic situation instances here...
]

GAMEPLAY_EVENTS = RANDOM_GAMEPLAY_EVENTS + DETERMINISTIC_GAMEPLAY_EVENTS

START_DELAY = 10  # seconds before situation manager starts

# Start random events in a background thread

def start_random_gameplay_events():
    def random_event_loop():
        time.sleep(random.uniform(10, 30))  # Wait a random time before first event
        while True:
            situation = random.choice(RANDOM_GAMEPLAY_EVENTS)
            situation.trigger()
            time.sleep(random.uniform(10, 30))
    thread = threading.Thread(target=random_event_loop, daemon=True)
    thread.start()

# Deterministic events are checked every second in the main/game loop or a separate thread

def start_deterministic_gameplay_events():
    def deterministic_event_loop():
        time.sleep(2)  # Wait 2 seconds at game start
        while True:
            for event in DETERMINISTIC_GAMEPLAY_EVENTS:
                event.trigger()
            time.sleep(1)  # Tick every second
    thread = threading.Thread(target=deterministic_event_loop, daemon=True)
    thread.start()

power_outage = PowerOutage()
climate_control = ClimateControl()
climate_control.start()
