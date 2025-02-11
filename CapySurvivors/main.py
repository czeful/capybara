# main.py
import pygame
import random
from game import settings
from game.menu import MainMenu, PauseMenu, OptionsMenu
from game.level import Level
from game.camera import Camera
from game.player import Player
from game.item import Item
from game.coin import Coin
from game.ui import UI
from game.enemy import StandardEnemy, FastEnemy, TankyEnemy, EasyBoss, HardBoss, Summon
from game.powerup import run_powerup_selection
from game.sounds import SoundManager
from game.bullet import Bullet  

sound_manager = SoundManager(volume=0.5)

def get_random_floor_position(level, max_attempts=100):
    for _ in range(max_attempts):
        x = random.randint(0, level.width - 1)
        y = random.randint(0, level.height - 1)
        dummy_rect = pygame.Rect(x, y, 1, 1)
        if not any(dummy_rect.colliderect(wall.rect) for wall in level.walls):
            return (x, y)
    return (level.width // 2, level.height // 2)

def game_end_panel(screen):
    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    button_rect = pygame.Rect(0, 0, 200, 50)
    button_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 100)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and button_rect.collidepoint(event.pos):
                    return
        screen.fill(settings.BLACK)
        message = font_large.render("Game Complete!", True, settings.WHITE)
        msg_rect = message.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 50))
        screen.blit(message, msg_rect)
        pygame.draw.rect(screen, settings.GRAY, button_rect)
        button_text = font_small.render("Main Menu", True, settings.WHITE)
        btn_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, btn_text_rect)
        pygame.display.flip()
        clock.tick(settings.FPS)

def run_game(screen, difficulty):
    if difficulty == "hard":
        level_file = "levels/level2.txt"
    else:
        level_file = "levels/level1.txt"
    level = Level(level_file, tile_size=50)
    if level.player_start is None:
        player_spawn = (level.width // 2, level.height // 2)
    else:
        player_spawn = level.player_start

    player = Player(player_spawn)
    camera = Camera(level.width, level.height)
    # Center the camera at the player spawn point:
    camera.camera_rect.topleft = (player_spawn[0] - settings.SCREEN_WIDTH // 2,
                                  player_spawn[1] - settings.SCREEN_HEIGHT // 2)

    player_group = pygame.sprite.GroupSingle(player)
    enemy_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    boss_bullet_group = pygame.sprite.Group()
    item_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()
    ui = UI()
    score = 0
    next_powerup_score = 100

    # Set enemy spawn intervals and base speed.
    if difficulty == "hard":
        enemy_spawn_interval = 790
        item_spawn_interval = 15000
        coin_spawn_interval = 7000
        base_enemy_speed = 225
    else:
        enemy_spawn_interval = 890
        item_spawn_interval = 12000
        coin_spawn_interval = 7000
        base_enemy_speed = 175

    enemy_spawn_event = pygame.USEREVENT + 1
    pygame.time.set_timer(enemy_spawn_event, enemy_spawn_interval)
    item_spawn_event = pygame.USEREVENT + 2
    pygame.time.set_timer(item_spawn_event, item_spawn_interval)
    coin_spawn_event = pygame.USEREVENT + 3
    pygame.time.set_timer(coin_spawn_event, coin_spawn_interval)

    # Define a new event for laser auto-fire.
    laser_shoot_event = pygame.USEREVENT + 4
    laser_timer_set = False

    # Variables for freezer effect.
    freezer_effect_active = False
    freezer_timer = 0.0

    # Create a static “paused” background for the dialogue scene.
    screen.fill(settings.BLACK)
    level.draw(screen, camera)
    for spr in player_group:
        screen.blit(spr.image, camera.apply(spr))
    pygame.display.flip()
    background_surface = screen.copy()

    # Import and run the dialogue scene.
    from game.dialog import run_dialog_scene
    run_dialog_scene(screen, background_surface)

    clock = pygame.time.Clock()
    running = True
    boss_spawned = False

    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        # Update freezer effect.
        if freezer_effect_active:
            freezer_timer -= dt
            if freezer_timer <= 0:
                freezer_effect_active = False
                freezer_timer = 0
                # Restore speeds of affected (non‐boss) enemies.
                for enemy in enemy_group:
                    if not isinstance(enemy, (EasyBoss, HardBoss)):
                        if hasattr(enemy, "original_speed"):
                            enemy.speed = enemy.original_speed
                effective_enemy_speed = base_enemy_speed
            else:
                effective_enemy_speed = base_enemy_speed - 75
                for enemy in enemy_group:
                    if not isinstance(enemy, (EasyBoss, HardBoss)):
                        if not hasattr(enemy, "original_speed"):
                            enemy.original_speed = enemy.speed
                        enemy.speed = enemy.original_speed - 75
        else:
            effective_enemy_speed = base_enemy_speed

        # Set laser timer event if the player has the laser powerup.
        if player.has_laser and not laser_timer_set:
            pygame.time.set_timer(laser_shoot_event, 4000)  # every 4 seconds
            laser_timer_set = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == enemy_spawn_event:
                roll = random.random()
                if roll < 0.50:
                    enemy = StandardEnemy.spawn(pygame.Rect(0, 0, level.width, level.height), player, speed=effective_enemy_speed)
                elif roll < 0.75:
                    enemy = FastEnemy.spawn(pygame.Rect(0, 0, level.width, level.height), player, speed=effective_enemy_speed + 150)
                else:
                    enemy = TankyEnemy.spawn(pygame.Rect(0, 0, level.width, level.height), player, speed=effective_enemy_speed - 100)
                enemy_group.add(enemy)
            elif event.type == item_spawn_event:
                pos = get_random_floor_position(level)
                # 10% chance to spawn "freezer"; otherwise "heal" or "speed".
                r = random.randint(1, 100)
                if r <= 10:
                    item_type = "freezer"
                else:
                    item_type = random.choice(["heal", "speed"])
                item = Item(pos, item_type)
                item_group.add(item)
            elif event.type == coin_spawn_event:
                pos = get_random_floor_position(level)
                coin = Coin(pos)
                coin_group.add(coin)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu = PauseMenu(screen)
                    choice = pause_menu.run()
                    _ = clock.tick(settings.FPS)
                    if choice == "continue":
                        pass
                    elif choice == "options":
                        options_menu = OptionsMenu(screen)
                        options_menu.run()
                        _ = clock.tick(settings.FPS)
                    elif choice == "quit to main menu":
                        return "main_menu"
            elif event.type == laser_shoot_event:
                if player.has_laser:
                    # Use the camera to get the player's current screen position.
                    player_screen_rect = camera.apply(player)
                    player_screen_pos = pygame.Vector2(player_screen_rect.center)
                    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                    direction = mouse_pos - player_screen_pos
                    if direction.length() == 0:
                        direction = pygame.Vector2(0, -1)
                    else:
                        direction = direction.normalize()
                    # Offset so that the laser starts at the edge of the player's sprite.
                    offset = direction * (player.rect.width / 2)
                    # Note: player.pos is in world coordinates.
                    start_pos = player.pos + offset
                    from game.bullet import LaserBullet  # Ensure LaserBullet is imported.
                    laser_bullet = LaserBullet(start_pos, direction, player.bullet_speed)
                    bullet_group.add(laser_bullet)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    global_mouse = pygame.Vector2(event.pos) + pygame.Vector2(camera.camera_rect.topleft)
                    bullets = player.shoot(global_mouse)
                    if bullets:
                        for bullet in bullets:
                            bullet_group.add(bullet)

        # Spawn boss when score threshold reached.
        if score >= 750 and not boss_spawned:
            boss_pos = StandardEnemy._spawn_position(pygame.Rect(0, 0, level.width, level.height))
            if difficulty == "hard":
                boss = HardBoss(boss_pos, player, boss_bullet_group, enemy_group, sound_manager)
            else:
                boss = EasyBoss(boss_pos, player, boss_bullet_group)
            enemy_group.add(boss)
            boss_spawned = True

        keys_pressed = pygame.key.get_pressed()
        player_group.update(dt, keys_pressed, level.walls)
        enemy_group.update(dt)
        bullet_group.update(dt)
        boss_bullet_group.update(dt)
        item_group.update(dt)
        coin_group.update(dt)

        for bullet in bullet_group:
            if pygame.sprite.spritecollideany(bullet, level.walls):
                bullet.kill()

        for bullet in bullet_group:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemy_group, False)
            if hit_enemies:
                for enemy in hit_enemies:
                    if getattr(bullet, "is_laser", False):
                        # For laser bullets, damage each enemy only once.
                        if id(enemy) not in bullet.damaged_enemies:
                            if enemy.take_damage(1):
                                if isinstance(enemy, EasyBoss):
                                    score += 100
                                    sound_manager.play_sound("boss_kill")
                                elif isinstance(enemy, HardBoss):
                                    score += 200
                                    sound_manager.play_sound("boss_kill")
                                elif isinstance(enemy, Summon):
                                    score += 5
                                    sound_manager.play_sound("enemy_kill")
                                else:
                                    score += 10
                                    sound_manager.play_sound("enemy_kill")
                            bullet.damaged_enemies.add(id(enemy))
                    else:
                        if enemy.take_damage(1):
                            if isinstance(enemy, EasyBoss):
                                score += 100
                                sound_manager.play_sound("boss_kill")
                            elif isinstance(enemy, HardBoss):
                                score += 200
                                sound_manager.play_sound("boss_kill")
                            elif isinstance(enemy, Summon):
                                score += 5
                                sound_manager.play_sound("enemy_kill")
                            else:
                                score += 10
                                sound_manager.play_sound("enemy_kill")
                        bullet.kill()

        for bullet in boss_bullet_group:
            if pygame.sprite.collide_rect(bullet, player):
                player.take_damage(10)
                sound_manager.play_sound("enemy_collision")
                bullet.kill()

        hit_enemies = pygame.sprite.spritecollide(player, enemy_group, False)
        for enemy in hit_enemies:
            if isinstance(enemy, (EasyBoss, HardBoss)):
                player.health = 0
                sound_manager.play_sound("enemy_collision")
            else:
                player.take_damage(10)
                sound_manager.play_sound("enemy_collision")
                enemy.kill()

        hit_items = pygame.sprite.spritecollide(player, item_group, True)
        for item in hit_items:
            if item.item_type == "heal":
                player.health = player.max_hp
                sound_manager.play_sound("heal")
                player.add_effect("heal")
            elif item.item_type == "speed":
                player.apply_speed_boost(10, 100)
                player.add_effect("speed")
                sound_manager.play_sound("speed")
            elif item.item_type == "freezer":
                if not freezer_effect_active:
                    freezer_effect_active = True
                    freezer_timer = 7.0
                    sound_manager.play_sound("freezer")
                    player.add_effect("freezer")

        hit_coins = pygame.sprite.spritecollide(player, coin_group, True)
        for coin in hit_coins:
            score += 10
            player.add_effect("coin")
            sound_manager.play_sound("coin")

        # Check if any boss (EasyBoss or HardBoss) is still alive.
        boss_alive = any(isinstance(enemy, (EasyBoss, HardBoss)) for enemy in enemy_group)
        # Only end the game when the score is 1500+ AND the boss is dead.
        if score >= 1500 and not boss_alive:
            game_end_panel(screen)
            return "main_menu"

        if score >= next_powerup_score:
            background_surface = screen.copy()
            chosen_boost = run_powerup_selection(screen, background_surface, enemy_group, player)
            player.apply_boost(chosen_boost)
            next_powerup_score += 100
            _ = clock.tick(60)

        camera.update(player)

        # Add any auto-shotgun and laser bullets from the player.
        if player.has_shotgun and player.shotgun_bullets:
            for bullet in player.shotgun_bullets:
                bullet_group.add(bullet)
            player.shotgun_bullets.clear()

        if player.has_laser and player.laser_bullets:
            for laser in player.laser_bullets:
                bullet_group.add(laser)
            player.laser_bullets.clear()
        
        # --- Drawing ---
        screen.fill(settings.BLACK)
        level.draw(screen, camera)

        for enemy in enemy_group:
            screen.blit(enemy.image, camera.apply(enemy))
            if isinstance(enemy, (EasyBoss, HardBoss)):
                enemy.draw_hp_bar(screen, camera)

        # If freezer effect is active, draw a translucent light blue overlay over the screen.
        if freezer_effect_active:
            overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((173, 216, 230, 100))  # light blue tint with alpha 100
            screen.blit(overlay, (0, 0))

        # Draw the player last so it is not tinted.
        for spr in player_group:
            screen.blit(spr.image, camera.apply(spr))
            spr.draw_effects(screen, camera)

        for bullet in bullet_group:
            screen.blit(bullet.image, camera.apply(bullet))
        for bullet in boss_bullet_group:
            screen.blit(bullet.image, camera.apply(bullet))
        for item in item_group:
            screen.blit(item.image, camera.apply(item))
        for coin in coin_group:
            screen.blit(coin.image, camera.apply(coin))

        ui.draw_status(screen, player, score)
        pygame.display.flip()

        if player.health <= 0:
            ui.draw_message(screen, "Game Over", settings.RED)
            pygame.display.flip()
            pygame.time.delay(2000)
            return "main_menu"

    return "quit"

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT = screen.get_size()
    pygame.display.set_caption("Vampire Survivors Inspired Game")
    sound_manager.play_background_music()
    pygame.mixer.music.set_volume(0.1)

    current_state = settings.STATE_MAIN_MENU
    running = True
    while running:
        if current_state == settings.STATE_MAIN_MENU:
            main_menu = MainMenu(screen)
            choice = main_menu.run()
            if choice in ["easy", "hard"]:
                current_state = settings.STATE_GAME
                result = run_game(screen, choice)
                if result == "main_menu":
                    current_state = settings.STATE_MAIN_MENU
                elif result == "quit":
                    running = False
            elif choice == "options":
                options_menu = OptionsMenu(screen)
                options_menu.run()
                current_state = settings.STATE_MAIN_MENU
            elif choice == "quit":
                running = False
        elif current_state == settings.STATE_GAME:
            result = run_game(screen, "easy")
            if result == "main_menu":
                current_state = settings.STATE_MAIN_MENU
            elif result == "quit":
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()
