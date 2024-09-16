import pygame
import math
from constants import (
    sword_img_full, font, WHITE, GRAY, GREEN, BLUE, PURPLE, ORANGE,
    ITEM_PRICES
)

class Item:
    def __init__(self, name, image, level=1):
        self.name = name
        self.full_image = image  # Full-size image
        self.image = pygame.transform.scale(image, (50, 50))  # Resize to slot size
        self.rect = self.image.get_rect()
        self.level = level

    def draw(self, surface, position, dragging=False):
        if dragging:
            # Draw full-size image when dragging
            surface.blit(self.full_image, position)
        else:
            # Draw resized image in slots
            surface.blit(self.image, position)
            # Draw border around the item based on its level
            border_color = get_border_color(self.level)
            pygame.draw.rect(surface, border_color, (position[0], position[1], 50, 50), 3)
            # Draw level number inside the icon at the top-left corner
            level_text = font.render(f"{self.level}", True, WHITE)
            surface.blit(level_text, (position[0] + 2, position[1] + 2))

    def to_dict(self):
        return {
            'name': self.name,
            'level': self.level
        }

    @staticmethod
    def from_dict(data):
        if data['name'] == 'sword':
            image = sword_img_full
            return Item(data['name'], image, data['level'])
        else:
            return None

def get_border_color(level):
    if 1 <= level <= 4:
        return GRAY
    elif 5 <= level <= 9:
        return GREEN
    elif 10 <= level <= 14:
        return BLUE
    elif 15 <= level <= 19:
        return PURPLE
    elif level >= 20:
        return ORANGE
    else:
        return WHITE  # Default color

def calculate_sell_price(item):
    base_price = ITEM_PRICES[item.name]
    return int(base_price * math.exp(item.level - 1))