import pygame
import os
import json
from constants import (
    WIDTH, HEIGHT, BLACK, WHITE, GRAY, DARK_GRAY, font, large_font, SAVE_DIR
)
from notifications import add_notification

def draw_main_menu(screen, in_main_menu):
    screen.fill(BLACK)
    menu_title = large_font.render("Main Menu", True, WHITE)
    screen.blit(menu_title, (WIDTH // 2 - menu_title.get_width() // 2, 100))

    # Buttons
    buttons = []
    # Depending on where we are, adjust the menu options
    if in_main_menu:
        options = ["New Game", "Load", "Exit"]
    else:
        options = ["Return", "Save", "Load", "New Game", "Exit"]

    for i, option in enumerate(options):
        button_rect = pygame.Rect(WIDTH // 2 - 100, 200 + i * 80, 200, 50)
        pygame.draw.rect(screen, GRAY, button_rect)
        button_text = font.render(option, True, WHITE)
        screen.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width()) // 2,
                                  button_rect.y + (button_rect.height - button_text.get_height()) // 2))
        buttons.append((option, button_rect))

    return buttons

def draw_save_files_menu(screen, files):
    screen.fill(BLACK)
    menu_title = large_font.render("Load Game", True, WHITE)
    screen.blit(menu_title, (WIDTH // 2 - menu_title.get_width() // 2, 50))

    buttons = []

    for i, filename in enumerate(files):
        button_rect = pygame.Rect(WIDTH // 2 - 200, 150 + i * 60, 400, 50)
        pygame.draw.rect(screen, GRAY, button_rect)
        button_text = font.render(filename, True, WHITE)
        screen.blit(button_text, (button_rect.x + 10, button_rect.y + (button_rect.height - button_text.get_height()) // 2))
        buttons.append((filename, button_rect))

    # Back button
    back_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 80, 100, 40)
    pygame.draw.rect(screen, GRAY, back_button_rect)
    back_text = font.render("Back", True, WHITE)
    screen.blit(back_text, (back_button_rect.x + (back_button_rect.width - back_text.get_width()) // 2,
                            back_button_rect.y + (back_button_rect.height - back_text.get_height()) // 2))
    buttons.append(("Back", back_button_rect))

    return buttons

def draw_save_menu(screen, save_name_input, existing_saves):
    screen.fill(BLACK)
    menu_title = large_font.render("Save Game", True, WHITE)
    screen.blit(menu_title, (WIDTH // 2 - menu_title.get_width() // 2, 50))

    # Input field for save name
    input_rect = pygame.Rect(WIDTH // 2 - 200, 150, 400, 40)
    pygame.draw.rect(screen, WHITE, input_rect, 2)
    input_text = font.render(save_name_input, True, WHITE)
    screen.blit(input_text, (input_rect.x + 10, input_rect.y + 10))

    # Label for input field
    input_label = font.render("Save Name:", True, WHITE)
    screen.blit(input_label, (input_rect.x, input_rect.y - 25))

    # Existing saves list
    buttons = []

    for i, filename in enumerate(existing_saves):
        button_rect = pygame.Rect(WIDTH // 2 - 200, 210 + i * 50, 400, 40)
        pygame.draw.rect(screen, GRAY, button_rect)
        button_text = font.render(filename[:-5], True, WHITE)  # Remove '.json' extension
        screen.blit(button_text, (button_rect.x + 10, button_rect.y + 10))
        buttons.append((filename, button_rect))

    # Save button
    save_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 100, 100, 40)
    pygame.draw.rect(screen, GRAY, save_button_rect)
    save_text = font.render("Save", True, WHITE)
    screen.blit(save_text, (save_button_rect.x + (save_button_rect.width - save_text.get_width()) // 2,
                            save_button_rect.y + (save_button_rect.height - save_text.get_height()) // 2))

    # Back button
    back_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 50, 100, 40)
    pygame.draw.rect(screen, GRAY, back_button_rect)
    back_text = font.render("Back", True, WHITE)
    screen.blit(back_text, (back_button_rect.x + (back_button_rect.width - back_text.get_width()) // 2,
                            back_button_rect.y + (back_button_rect.height - back_text.get_height()) // 2))

    # Return the interactive elements
    return input_rect, buttons, save_button_rect, back_button_rect

def save_game(player_balance, inventory_slots, anvil_item, save_name):
    save_data = {
        'player_balance': player_balance,
        'inventory_slots': [item.to_dict() if item else None for item in inventory_slots],
        'anvil_item': anvil_item.to_dict() if anvil_item else None,
    }
    filename = f"{save_name}.json"
    filepath = os.path.join(SAVE_DIR, filename)
    file_exists = os.path.exists(filepath)
    with open(filepath, 'w') as f:
        json.dump(save_data, f)
    add_notification(f"Game saved as '{save_name}'.")
    return file_exists  # Return whether the file existed before

def load_game(filename):
    with open(os.path.join(SAVE_DIR, filename), 'r') as f:
        save_data = json.load(f)
    add_notification(f"Game loaded from '{filename[:-5]}'.")
    return save_data