# game/sounds.py
import pygame
import os

class SoundManager:
    def __init__(self, volume=0.5):
        self.volume = volume

        # Initialize the mixer; you can also set the frequency, size, channels, and buffer if desired.
        pygame.mixer.init()

        # Load background music.
        # Ensure the file exists in the assets/sounds folder.
        self.background_music = os.path.join("assets", "sounds", "background.mp3")
        
        # Dictionary to hold various sound effects.
        self.sounds = {}
        try:
            self.sounds["coin"] = pygame.mixer.Sound(os.path.join("assets", "sounds", "coin.mp3"))
            self.sounds["heal"] = pygame.mixer.Sound(os.path.join("assets", "sounds", "heal.mp3"))
            self.sounds["speed"] = pygame.mixer.Sound(os.path.join("assets", "sounds", "speed.mp3"))
            self.sounds["freezer"] = pygame.mixer.Sound(os.path.join("assets", "sounds", "freezer.mp3"))
            self.sounds["enemy_collision"] = pygame.mixer.Sound(os.path.join("assets", "sounds", "enemy_collision.mp3"))
            self.sounds["enemy_kill"] = pygame.mixer.Sound(os.path.join("assets", "sounds", "enemy_kill.mp3"))
            self.sounds["boss_kill"] = pygame.mixer.Sound(os.path.join("assets", "sounds", "boss_kill.mp3"))
            self.sounds["player_hit"] = pygame.mixer.Sound(os.path.join("assets", "sounds", "player_hit.mp3"))
            self.sounds["hardboss_shoot"] = pygame.mixer.Sound(os.path.join("assets", "sounds", "hardboss_shoot.mp3"))
        except Exception as e:
            print("Error loading sound effect:", e)

        # Set volume for each sound effect.
        for key, sound in self.sounds.items():
            sound.set_volume(self.volume)

    def play_background_music(self):
        """Plays background music on an infinite loop."""
        try:
            pygame.mixer.music.load(self.background_music)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Error playing background music:", e)

    def play_sound(self, key):
        """Plays the sound effect corresponding to the given key (e.g., 'coin', 'heal')."""
        if key in self.sounds:
            self.sounds[key].play()
        else:
            print(f"Sound '{key}' not found.")
