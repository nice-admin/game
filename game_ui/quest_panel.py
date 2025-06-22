import pygame

ONSCREEN_RIGHT_MARGIN = 0.15
ONSCREEN_TOP_MARGIN = 0.35
QUEST_PANEL_WIDTH = 300

class Checkmark:
    def __init__(self, size=15):
        self.size = size

    def draw(self, surface, x, y, color=(200, 200, 200), thickness=2):
        pygame.draw.rect(surface, color, (x, y, self.size, self.size), thickness)

class QuestDisplayItem:
    def __init__(self, header, objectives, completed=False, reward=None, quest_id=None):
        self.header = header
        self.objectives = objectives  # List of dicts: {desc, current, required}
        self.completed = completed
        self.reward = reward
        self.quest_id = quest_id

    def get_wrapped_objective_lines(self, font, max_width=QUEST_PANEL_WIDTH):
        lines = []
        for obj in self.objectives:
            progress = f"{obj.get('current', 0)}/{obj.get('required', 1)} " if 'current' in obj and 'required' in obj else ''
            desc = obj['desc']
            text = progress + desc
            words = text.split()
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surf = font.render(test_line, True, (200, 200, 200))
                if test_surf.get_width() > max_width:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
        return lines

    def draw(self, surface, y=None, width=QUEST_PANEL_WIDTH, header_font=None, text_font=None):
        surf_w, surf_h = surface.get_width(), surface.get_height()
        if header_font is None:
            header_font = pygame.font.SysFont(None, 28)
        if text_font is None:
            text_font = pygame.font.SysFont(None, 24)
        header_surf = header_font.render(self.header, True, (255, 255, 255))
        x = int(surf_w * (1 - ONSCREEN_RIGHT_MARGIN))
        if y is None:
            y = int(surf_h * 0.5 - (header_surf.get_height() + 10 + len(self.get_wrapped_objective_lines(text_font, QUEST_PANEL_WIDTH))*24) // 2)
        surface.blit(header_surf, (x, y))
        checkmark = Checkmark()
        line_y = y + 30
        for obj in self.objectives:
            # Prepare wrapped lines for this objective
            progress = f"{obj.get('current', 0)}/{obj.get('required', 1)} " if 'current' in obj and 'required' in obj else ''
            desc = obj['desc']
            text = progress + desc
            words = text.split()
            current_line = ""
            lines = []
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surf = text_font.render(test_line, True, (200, 200, 200))
                if test_surf.get_width() > QUEST_PANEL_WIDTH:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            # Draw lines for this objective
            for i, line in enumerate(lines):
                if i == 0:
                    check_x = x + 15
                    check_y = line_y + (text_font.get_height() - checkmark.size) // 2
                    checkmark.draw(surface, check_x, check_y)
                    text_x = check_x + checkmark.size + 5
                else:
                    text_x = x + 15 + checkmark.size + 5
                text_surf = text_font.render(line, True, (200, 200, 200))
                surface.blit(text_surf, (text_x, line_y))
                line_y += 24

def draw_quest_panel(surface, active_deterministic, active_random):
    surf_h = surface.get_height()
    start_y = int(surf_h * ONSCREEN_TOP_MARGIN)  # Start at defined top margin ratio of the screen height
    y = start_y
    text_font = pygame.font.SysFont(None, 24)
    # Draw active deterministic quests first
    for quest in active_deterministic:
        lines = quest.get_wrapped_objective_lines(text_font)
        quest.draw(surface, y=y)
        y += 30 + len(lines)*24 + 10
    # Add extra spacing before random quests if both exist
    if active_deterministic and active_random:
        y += 20
    # Draw active random quests below
    for quest in active_random:
        lines = quest.get_wrapped_objective_lines(text_font)
        quest.draw(surface, y=y)
        y += 30 + len(lines)*24 + 10

random_quests = [
    QuestDisplayItem(
        header="Teamwork",
        objectives=[{"desc": "Finish a single project", "current": 0, "required": 1}],
        completed=False,
        reward="Bonus productivity"
    ),
    QuestDisplayItem(
        header="Office of the century",
        objectives=[{"desc": "Maintain Heavenly Office Quality status for a week"}],
        completed=False,
        reward="Employee happiness boost"
    ),
]

deterministic_quests = [
    QuestDisplayItem(
        header="First Steps",
        objectives=[
            {"desc": "Hire artist and allow him to complete a single task successfully.", "current": 0, "required": 5},
        ],
        completed=False,
        reward="100 coins",
        quest_id=1
    ),
    QuestDisplayItem(
        header="Power Up",
        objectives=[{"desc": "Reach Breaker Limit higher than 20 KW", "current": 0, "required": 1}],
        completed=False,
        reward="Unlock new equipment",
        quest_id=2
    ),
]

# Will be set by gameplay_events. Initially empty.
active_quests = []
random_active_quests = []
