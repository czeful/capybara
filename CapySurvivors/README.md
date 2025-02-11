# 2D Action Game

## Overview
This project is a 2D action game built with Python and Pygame. The game features animated character movement, enemy pursuit, item and coin collection, powerup selection, boos fights, and adjustable difficulty levels. It is organized into modular components for easy maintenance and future expansion.

## Setup Instructions

1. **Install Python 3.x**  
   Make sure you have Python installed on your system.

2. **Install Dependencies**  
   Open a terminal or command prompt in the project’s root directory and run:
   ```bash
   pip install pygame

## Launch Instructions

1. **Run the game**  
    From the project root directory, launch the game by running: python main.py
2. **Select Difficulty**
    When the main menu appears, select either "easy" or "hard". The hard mode will load level2.txt and use faster enemy spawn and movement parameters.
3. **Contols**
    Movement: Use W, A, S, D keys.
    Shooting: Use the left mouse button to shoot in the direction of the cursor.
    Pause/Menu: Press ESC to access the pause menu.
    Items: pick up items and coins to get different temporary strengthenings.
    Power-ups: Every 100 score, select a power-up to strengthen yourself forever.
4. **Enjoy the Game!**
    Game ends when you reach 1500 score and defeat the boss. 