import pygame
from src.main_game import MainGame


if __name__ == "__main__":
    pygame.init()
    global main_game
    main_game = MainGame()
    main_game.start()
