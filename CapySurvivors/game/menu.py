import pygame
from game import settings
import json
import os

class MenuItem:
    def __init__(self, text, position, font, color=settings.WHITE, selected_color=settings.RED):
        self.text = text
        self.position = position
        self.font = font
        self.color = color
        self.selected_color = selected_color
        self.label = self.font.render(self.text, True, self.color)
        self.rect = self.label.get_rect(center=self.position)

    def draw(self, screen, is_selected):
        if is_selected:
            label = self.font.render(self.text, True, self.selected_color)
        else:
            label = self.font.render(self.text, True, self.color)
        screen.blit(label, self.rect)

    def is_mouse_over(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class BaseMenu:
    def __init__(self, screen, items, bg_color=settings.BLACK):
        self.screen = screen
        self.items = items  # List of MenuItem objects.
        self.bg_color = bg_color
        self.selected_index = 0

    def draw(self):
        # This basic draw method can be overridden.
        self.screen.fill(self.bg_color)
        for index, item in enumerate(self.items):
            is_selected = (index == self.selected_index)
            item.draw(self.screen, is_selected)
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        selected_option = None
        running = True
        while running:
            clock.tick(settings.FPS)
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    selected_option = "quit"
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    for index, item in enumerate(self.items):
                        if item.is_mouse_over(mouse_pos):
                            self.selected_index = index
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for index, item in enumerate(self.items):
                            if item.is_mouse_over(event.pos):
                                self.selected_index = index
                                selected_option = item.text.lower()
                                running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.items)
                    elif event.key == pygame.K_RETURN:
                        selected_option = self.items[self.selected_index].text.lower()
                        running = False
            self.draw()
        return selected_option

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 50)
        self.menu_items = []
        # --- Load background image ---
        try:
            self.bg_image = pygame.image.load("assets/images/main_menu_bg.png").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except Exception as e:
            print("Error loading main menu background:", e)
            self.bg_image = None
        # --- Load game name image ---
        try:
            self.game_name_img = pygame.image.load("assets/images/game_name.png").convert_alpha()
            self.game_name_img = pygame.transform.scale(self.game_name_img, (375, 275))
        except Exception as e:
            print("Error loading game name image:", e)
            self.game_name_img = self.font.render("GAME NAME", True, settings.WHITE)
        # --- Create a panel for menu options ---
        panel_width = int(settings.SCREEN_WIDTH * 0.4)
        panel_height = int(settings.SCREEN_HEIGHT * 0.4)
        panel_x = (settings.SCREEN_WIDTH - panel_width) // 2
        panel_y = settings.SCREEN_HEIGHT - panel_height - 50  # 50 pixels from the bottom
        self.panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        # --- Define menu options ---
        texts = ["Easy", "Hard", "Options", "Quit"]
        num_items = len(texts)
        spacing = panel_height / (num_items + 1)
        for i, text in enumerate(texts):
            pos_x = self.panel_rect.centerx
            pos_y = self.panel_rect.top + (i + 1) * spacing
            self.menu_items.append(MenuItem(text, (pos_x, pos_y), self.font))
        self.selected_index = 0

    def draw(self):
        # Draw the background image.
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(settings.BLACK)
        # Draw the game name image at the top center.
        game_name_rect = self.game_name_img.get_rect(midtop=(settings.SCREEN_WIDTH // 2, 5))
        self.screen.blit(self.game_name_img, game_name_rect)
        # Draw a semi-transparent black panel for the menu options.
        panel_surface = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 200))
        self.screen.blit(panel_surface, (self.panel_rect.x, self.panel_rect.y))
        # Draw each menu item onto the panel.
        for index, item in enumerate(self.menu_items):
            is_selected = (index == self.selected_index)
            item.draw(self.screen, is_selected)
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        selected_option = None
        running = True
        while running:
            clock.tick(settings.FPS)
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    selected_option = "quit"
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    for index, item in enumerate(self.menu_items):
                        if item.is_mouse_over(mouse_pos):
                            self.selected_index = index
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for index, item in enumerate(self.menu_items):
                            if item.is_mouse_over(event.pos):
                                self.selected_index = index
                                selected_option = item.text.lower()
                                running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN:
                        selected_option = self.menu_items[self.selected_index].text.lower()
                        running = False
            self.draw()
        return selected_option

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 50)
        self.menu_items = []
        # --- Load background image for the pause menu (reuse main menu bg) ---
        try:
            self.bg_image = pygame.image.load("assets/images/main_menu_bg.png").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except Exception as e:
            print("Error loading background for pause menu:", e)
            self.bg_image = None
        # --- Create a panel for the pause menu options ---
        panel_width = int(settings.SCREEN_WIDTH * 0.45)
        panel_height = int(settings.SCREEN_HEIGHT * 0.4)
        panel_x = (settings.SCREEN_WIDTH - panel_width) // 2
        panel_y = (settings.SCREEN_HEIGHT - panel_height) // 2  # Center the panel vertically
        self.panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        # --- Define pause menu options ---
        texts = ["Continue", "Options", "Quit to Main Menu"]
        num_items = len(texts)
        spacing = panel_height / (num_items + 1)
        for i, text in enumerate(texts):
            pos_x = self.panel_rect.centerx
            pos_y = self.panel_rect.top + (i + 1) * spacing
            self.menu_items.append(MenuItem(text, (pos_x, pos_y), self.font))
        self.selected_index = 0

    def draw(self):
        # Draw the background image if available; otherwise fill with black.
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(settings.BLACK)
        # Draw a semi–transparent panel for the menu options.
        panel_surface = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 200))
        self.screen.blit(panel_surface, (self.panel_rect.x, self.panel_rect.y))
        # Draw each menu item onto the panel.
        for index, item in enumerate(self.menu_items):
            is_selected = (index == self.selected_index)
            item.draw(self.screen, is_selected)
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        selected_option = None
        running = True
        while running:
            clock.tick(settings.FPS)
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    selected_option = "quit"
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    for index, item in enumerate(self.menu_items):
                        if item.is_mouse_over(mouse_pos):
                            self.selected_index = index
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for index, item in enumerate(self.menu_items):
                            if item.is_mouse_over(event.pos):
                                self.selected_index = index
                                selected_option = item.text.lower()
                                running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN:
                        selected_option = self.menu_items[self.selected_index].text.lower()
                        running = False
            self.draw()
        return selected_option

class OptionsMenu:
    """
    Options menu for adjusting sound settings.
    Volume is saved persistently to a JSON file.
    Adjust sound volume using LEFT/RIGHT arrow keys and confirm with ENTER.
    """
    def __init__(self, screen, config_file="config.json"):
        self.screen = screen
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)
        self.config_file = config_file
        self.volume = self.load_volume()
        # --- Load background image (reuse main menu background if available) ---
        try:
            self.bg_image = pygame.image.load("assets/images/main_menu_bg.png").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except Exception as e:
            print("Error loading background for options:", e)
            self.bg_image = None

    def load_volume(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    return data.get("volume", settings.DEFAULT_VOLUME)
            except Exception as e:
                print("Error loading config:", e)
                return settings.DEFAULT_VOLUME
        return settings.DEFAULT_VOLUME

    def save_volume(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump({"volume": self.volume}, f)
        except Exception as e:
            print("Error saving config:", e)

    def draw(self):
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(settings.BLACK)
        # Draw a semi-transparent panel for the options.
        panel_width = int(settings.SCREEN_WIDTH * 0.5)
        panel_height = int(settings.SCREEN_HEIGHT * 0.3)
        panel_x = (settings.SCREEN_WIDTH - panel_width) // 2
        panel_y = (settings.SCREEN_HEIGHT - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 200))
        self.screen.blit(panel_surface, (panel_rect.x, panel_rect.y))
        vol_text = self.font.render("Sound Volume: " + str(round(self.volume, 1)), True, settings.WHITE)
        instruction = self.small_font.render("Use LEFT/RIGHT to adjust, ENTER to confirm", True, settings.WHITE)
        vol_text_rect = vol_text.get_rect(center=(panel_rect.centerx, panel_rect.centery - 20))
        instruction_rect = instruction.get_rect(center=(panel_rect.centerx, panel_rect.centery + 30))
        self.screen.blit(vol_text, vol_text_rect)
        self.screen.blit(instruction, instruction_rect)
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(settings.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.volume = max(0.0, self.volume - 0.1)
                    elif event.key == pygame.K_RIGHT:
                        self.volume = min(1.0, self.volume + 0.1)
                    elif event.key == pygame.K_RETURN:
                        running = False
            self.draw()
        self.save_volume()
        pygame.mixer.music.set_volume(self.volume)
        return "options_saved"
