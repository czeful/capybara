import pygame
from game import settings

def run_dialog_scene(screen, background):
    """
    Displays a dialogue scene over a static background.
    
    - The dialog box occupies 1/4 of the screen height (change BOX_HEIGHT to adjust).
    - The character sprite appears above the dialog box on the right.
    - Each text message is animated letter-by-letter.
    - After the final message, the dialog slides off downward.
      Once the slide is complete, we clear the dialog so it does not reappear.
    """
    # --- Dialog box dimensions (change BOX_HEIGHT to adjust the size) ---
    BOX_WIDTH = settings.SCREEN_WIDTH
    BOX_HEIGHT = settings.SCREEN_HEIGHT // 4
    BOX_X = 0
    BOX_Y = settings.SCREEN_HEIGHT - BOX_HEIGHT

    messages = [
        "Good morning, soldier. As you may have noticed, \nthe zombies are starting to advance at an increasing speed.",
        "Take this gun. Press LMB to shoot it. \nUse it to clear this area of those freaks.",
        "Every 100 points you score, you will receive a random power-up. \nSome of them permanently give you new weapons. \nChoose wisely.",
        "Sometimes random items and coins will appear on the floor. \nItems give you various bonuses, \ncoins give you more score points.",
        "Earn 1500 points, defeat the boss and you are free."
    ]

    # --- Load the character sprite ---
    try:
        character_sprite = pygame.image.load("assets/images/character_dialog.png").convert_alpha()
        SPRITE_WIDTH, SPRITE_HEIGHT = 550, 650 
        character_sprite = pygame.transform.scale(character_sprite, (SPRITE_WIDTH, SPRITE_HEIGHT))
    except Exception as e:
        print("Error loading character sprite for dialogue:", e)
        SPRITE_WIDTH, SPRITE_HEIGHT = 400, 600
        character_sprite = pygame.Surface((SPRITE_WIDTH, SPRITE_HEIGHT))
        character_sprite.fill(settings.RED)

    # --- Calculate positions ---
    # Dialog box rectangle.
    dialog_box_rect = pygame.Rect(BOX_X, BOX_Y, BOX_WIDTH, BOX_HEIGHT)
    # The character sprite appears above the dialog box at the right side.
    sprite_x = settings.SCREEN_WIDTH - SPRITE_WIDTH - 10
    sprite_y = dialog_box_rect.top - SPRITE_HEIGHT 

    # --- Font setup for text ---
    font = pygame.font.Font(None, 72)

    # --- Variables for letter-by-letter animation ---
    current_message_index = 0
    current_full_text = messages[current_message_index]
    displayed_text = ""
    letter_index = 0
    LETTER_DELAY = 0.025  # seconds delay between letters (adjust to change speed)
    letter_timer = 0

    clock = pygame.time.Clock()
    running_dialog = True

    while running_dialog:
        dt = clock.tick(settings.FPS) / 1000.0  # seconds elapsed since last frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if letter_index < len(current_full_text):
                        # If the text is still animating, show the full text immediately.
                        letter_index = len(current_full_text)
                        displayed_text = current_full_text
                        letter_timer = 0
                    else:
                        # If full text is already shown:
                        if current_message_index < len(messages) - 1:
                            # Advance to the next message.
                            current_message_index += 1
                            current_full_text = messages[current_message_index]
                            displayed_text = ""
                            letter_index = 0
                            letter_timer = 0
                        else:
                            # --- Slide-off animation ---
                            slide_speed = 200  # pixels per second (adjust as needed)
                            slide_offset = 0
                            slide_running = True
                            while slide_running:
                                dt_slide = clock.tick(settings.FPS) / 1000.0
                                slide_offset += slide_speed * dt_slide
                                # Redraw the background.
                                screen.blit(background, (0, 0))
                                # Compute the new position for the dialog box.
                                new_box_rect = pygame.Rect(BOX_X, BOX_Y + slide_offset, BOX_WIDTH, BOX_HEIGHT)
                                dialog_box_surface = pygame.Surface((new_box_rect.width, new_box_rect.height), pygame.SRCALPHA)
                                dialog_box_surface.fill((0, 0, 0, 180))
                                screen.blit(dialog_box_surface, (new_box_rect.x, new_box_rect.y))
                                # Draw the (final) text.
                                lines = displayed_text.split('\n')
                                for i, line in enumerate(lines):
                                    text_surface = font.render(line, True, settings.WHITE)
                                    text_x = new_box_rect.x + 20
                                    text_y = new_box_rect.y + 20 + i * text_surface.get_height()
                                    screen.blit(text_surface, (text_x, text_y))
                                # Draw the character sprite, sliding down too.
                                new_sprite_y = sprite_y + slide_offset
                                screen.blit(character_sprite, (sprite_x, new_sprite_y))
                                pygame.display.flip()
                                # Once the dialog box is completely off the screen...
                                if new_box_rect.top >= settings.SCREEN_HEIGHT:
                                    slide_running = False
                                    running_dialog = False
                                    break
                            # --- Clear the dialog scene after sliding off ---
                            screen.blit(background, (0, 0))
                            pygame.display.flip()
                            break
        if not running_dialog:
            break

        # --- Letter-by-letter text animation update ---
        if letter_index < len(current_full_text):
            letter_timer += dt
            if letter_timer >= LETTER_DELAY:
                letter_timer = 0
                letter_index += 1
                displayed_text = current_full_text[:letter_index]

        # --- Draw the dialog scene ---
        screen.blit(background, (0, 0))
        dialog_box_surface = pygame.Surface((dialog_box_rect.width, dialog_box_rect.height), pygame.SRCALPHA)
        dialog_box_surface.fill((0, 0, 0, 180))
        screen.blit(dialog_box_surface, (dialog_box_rect.x, dialog_box_rect.y))
        lines = displayed_text.split('\n')
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, settings.WHITE)
            text_x = dialog_box_rect.x + 20
            text_y = dialog_box_rect.y + 20 + i * text_surface.get_height()
            screen.blit(text_surface, (text_x, text_y))
        screen.blit(character_sprite, (sprite_x, sprite_y))
        pygame.display.flip()

    # End of dialog scene – control returns to the game.

