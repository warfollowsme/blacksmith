import pygame
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Upgrader")

# Load images
anvil_img = pygame.image.load('anvil.png')
sword_img_full = pygame.image.load('sword.png')

# Resize images if necessary
anvil_img = pygame.transform.scale(anvil_img, (100, 100))

# Fonts
font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 48)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)

# Item prices
ITEM_PRICES = {
    'sword': 500,
    'upgrade_kit': 1000  # Cost deducted during upgrade
}

# Paths
SAVE_DIR = 'saves'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)