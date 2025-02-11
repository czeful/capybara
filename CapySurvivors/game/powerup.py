# game/powerup.py
import pygame
import random
from game import settings

class PowerupCard:
    def __init__(self, boost_type):
        self.boost_type = boost_type
        if boost_type == "max_hp":
            self.name = "Unity with Nature"
            self.description = "Increase maximum health by 5."
            self.color = (255, 100, 100)  # light red
            self.image_path = "assets/images/powerups/max_hp.png"
        elif boost_type == "speed":
            self.name = "Speed. I am Speed."
            self.description = "Increase your movement speed."
            self.color = (100, 255, 100)  # light green
            self.image_path = "assets/images/powerups/speed.png"
        elif boost_type == "bullet_speed":
            self.name = "War. War never changes."
            self.description = "Increase bullet speed."
            self.color = (100, 100, 255)  # light blue
            self.image_path = "assets/images/powerups/bullet_speed.png"
        elif boost_type == "bullet_count":
            self.name = "Dangerous Jackpot"
            self.description = "Increase bullets per shot by 1."
            self.color = (255, 255, 100)  # light yellow
            self.image_path = "assets/images/powerups/bullet_count.png"
        elif boost_type == "shield":
            self.name = "My life is your shield"
            self.description = "Gain a shield that prevents \ndamage for 7 seconds."
            self.color = (173, 216, 230)  # light blue
            self.image_path = "assets/images/powerups/shield.png"
        elif boost_type == "shotgun":
            self.name = "Powder ring"
            self.description = "Every 5 seconds, shoot 8 bullets \naround you."
            self.color = (255, 165, 0)  # orange
            self.image_path = "assets/images/powerups/shotgun.png"
        elif boost_type == "laser":
            self.name = "Pierce the heavens"
            self.description = "Automatically fire a piercing \nbullet every 4 seconds."
            self.color = (176, 97, 97)  
            self.image_path = "assets/images/powerups/laser.png"
        else:
            self.name = "Unknown"
            self.description = ""
            self.color = (200, 200, 200)
            self.image_path = None

        self.width = 340
        self.height = 520  # Increased height by 20 pixels
        self.rect = pygame.Rect(0, 0, self.width, self.height)

        self.select_button_rect = pygame.Rect(0, 0, 100, 40)
        self.select_button_rect.centerx = self.width // 2
        self.select_button_rect.top = self.height - 50

        if self.image_path:
            try:
                self.powerup_image = pygame.image.load(self.image_path).convert_alpha()
                self.powerup_image = pygame.transform.scale(self.powerup_image, (300, 300))
            except Exception as e:
                print("Error loading powerup image:", e)
                self.powerup_image = None
        else:
            self.powerup_image = None

    def draw(self, surface):
        card_surface = pygame.Surface((self.width, self.height))
        card_surface.fill(self.color)
        pygame.draw.rect(card_surface, settings.WHITE, card_surface.get_rect(), 4)
        font_title = pygame.font.Font(None, 32)
        font_desc = pygame.font.Font(None, 24)
        font_button = pygame.font.Font(None, 28)
        name_text = font_title.render(self.name, True, settings.BLACK)
        card_surface.blit(name_text, (10, 10))
        if self.powerup_image:
            image_rect = self.powerup_image.get_rect()
            image_rect.topleft = (10, 50)
            card_surface.blit(self.powerup_image, image_rect)
        else:
            placeholder_rect = pygame.Rect(10, 50, 150, 150)
            pygame.draw.rect(card_surface, settings.WHITE, placeholder_rect, 2)
        
        # Handle multiline text rendering for the description
        desc_lines = self.description.split('\n')
        y_offset = 360  # Adjusted Y offset
        for line in desc_lines:
            desc_text = font_desc.render(line, True, settings.BLACK)
            card_surface.blit(desc_text, (10, y_offset))
            y_offset += desc_text.get_height() + 5
        
        pygame.draw.rect(card_surface, settings.GRAY, self.select_button_rect)
        pygame.draw.rect(card_surface, settings.WHITE, self.select_button_rect, 2)
        button_text = font_button.render("Select", True, settings.WHITE)
        btn_text_rect = button_text.get_rect(center=self.select_button_rect.center)
        card_surface.blit(button_text, btn_text_rect)
        surface.blit(card_surface, self.rect.topleft)
    
    def get_select_button_rect_absolute(self):
        return pygame.Rect(
            self.rect.left + self.select_button_rect.left,
            self.rect.top + self.select_button_rect.top,
            self.select_button_rect.width,
            self.select_button_rect.height
        )

def get_random_boost(player):
    #Add "laser" to the list of possible boosts.
    options = ["shield", "shotgun", "laser", "max_hp", "speed", "bullet_speed", "bullet_count"]
    weights = [0.15, 0.10, 0.10, 0.45, 0.45, 0.35, 0.05]  

    if getattr(player, "has_shotgun", False):
        weights[1] = 0  # Do not offer shotgun if already acquired.
    if getattr(player, "has_laser", False):
        weights[2] = 0
    chosen_boost = random.choices(options, weights)[0]
    return chosen_boost

def run_powerup_selection(screen, background_surface, enemy_group, player):
    clock = pygame.time.Clock()
    card1_type = get_random_boost(player)
    card2_type = get_random_boost(player)
    while card2_type == card1_type:
        card2_type = get_random_boost(player)
    card1 = PowerupCard(card1_type)
    card2 = PowerupCard(card2_type)
    screen_width, screen_height = screen.get_size()
    card1.rect.center = (screen_width // 3, screen_height // 2)
    card2.rect.center = (2 * screen_width // 3, screen_height // 2)

    for enemy in enemy_group:
        enemy.paused = True
    
    selected = None
    while selected is None:
        clock.tick(settings.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if card1.get_select_button_rect_absolute().collidepoint(pos):
                    selected = card1.boost_type
                elif card2.get_select_button_rect_absolute().collidepoint(pos):
                    selected = card2.boost_type
        
        screen.blit(background_surface, (0, 0))
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 36)
        instruct = font.render("Choose a Powerup!", True, settings.WHITE)
        screen.blit(instruct, (screen_width // 2 - instruct.get_width() // 2, 50))
        card1.draw(screen)
        card2.draw(screen)
        pygame.display.flip()
        for enemy in enemy_group:
             enemy.paused = False
    return selected
