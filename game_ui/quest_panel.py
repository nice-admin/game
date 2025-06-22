import pygame

ONSCREEN_TOP_MARGIN = 0.35  # Ratio for top margin placement of quest panel
ONSCREEN_RIGHT_MARGIN = 0.17  # Ratio for right margin placement (20% from the right)

class QuestDisplayItem:
    def __init__(self, name, objective, completed=False, reward=None, quest_id=None):
        self.name = name
        self.objective = objective
        self.completed = completed
        self.reward = reward
        self.quest_id = quest_id

    def get_wrapped_objective_lines(self, font, max_width=400):
        words = self.objective.split()
        lines = []
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

    def draw(self, surface, y=None, width=400, header_font=None, text_font=None):
        surf_w, surf_h = surface.get_width(), surface.get_height()
        if header_font is None:
            header_font = pygame.font.SysFont(None, 28)
        if text_font is None:
            text_font = pygame.font.SysFont(None, 24)
        header_surf = header_font.render(self.name, True, (255, 255, 255))
        lines = self.get_wrapped_objective_lines(text_font)
        x = int(surf_w * (1 - ONSCREEN_RIGHT_MARGIN))
        if y is None:
            y = int(surf_h * 0.5 - (header_surf.get_height() + 10 + len(lines)*24) // 2)
        surface.blit(header_surf, (x, y))
        for i, line in enumerate(lines):
            text_surf = text_font.render(line, True, (200, 200, 200))
            surface.blit(text_surf, (x + 15, y + 30 + i * 24))  # Add 10px margin to the right for quest text

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
        name="Teamwork",
        objective="Finish a single project",
        completed=False,
        reward="Bonus productivity"
    ),
    QuestDisplayItem(
        name="Office of the century",
        objective="Maintain Heavenly Office Quality status  for a week",
        completed=False,
        reward="Employee happiness boost"
    ),
]

deterministic_quests = [
    QuestDisplayItem(
        name="First Steps",
        objective="Hire artist and allow him to complete a single task succesfully.",
        completed=False,
        reward="100 coins",
        quest_id=1
    ),
    QuestDisplayItem(
        name="Power Up",
        objective="Reach Breaker Limit higher than 20 KW",
        completed=False,
        reward="Unlock new equipment",
        quest_id=2
    ),
]

# Will be set by gameplay_events. Initially empty.
active_quests = []
random_active_quests = []
