import pygame
import sys
import random
import math
import json
import os
import datetime

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Upgrader")

# Load images
anvil_img = pygame.image.load('anvil.png')
sword_img_full = pygame.image.load('sword.png')
# Resize the anvil image if necessary
anvil_img = pygame.transform.scale(anvil_img, (100, 100))

# Fonts
font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 48)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)

# Player balance
player_balance = 5000

# Item prices
ITEM_PRICES = {
    'sword': 500,
    'upgrade_kit': 1000  # Cost deducted during upgrade
}

# Inventory
initial_inventory_slots = 5
max_inventory_slots = 30
inventory_slots = [None] * initial_inventory_slots  # Start with 5 slots
inventory_slot_cost = 5000  # Initial cost for additional slot

# Shop inventory
shop_inventory = {
    'sword': {'image': sword_img_full, 'price': ITEM_PRICES['sword']},
    'slot': {'image': None, 'price': inventory_slot_cost},  # Slot purchase
}

# Anvil slot
anvil_item = None  # Only one slot now

# Positions
anvil_pos = (WIDTH // 2 - anvil_img.get_width() // 2, HEIGHT // 2 - anvil_img.get_height() // 2 - 50)
upgrade_button_rect = pygame.Rect(WIDTH // 2 - 40, anvil_pos[1] + anvil_img.get_height() + 80, 80, 40)

# Slot position (centered below the anvil)
slot_y = anvil_pos[1] + anvil_img.get_height() + 10
slot_x_item = WIDTH // 2 - 25  # Centered slot

# Game Over variables
game_over = False
restart_button_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 30, 120, 40)

# Menu variables
in_main_menu = True
in_game_menu = False
in_load_menu = False

# Menu buttons
menu_buttons = []
save_files = []

# Dragging variables
dragging_item = None
drag_offset = (0, 0)
dragging_full_size_image = None

# Paths
SAVE_DIR = 'saves'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Item class
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

# Function to get border color based on item level
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

# Function to calculate sell price
def calculate_sell_price(item):
    base_price = ITEM_PRICES[item.name]
    return int(base_price * math.exp(item.level - 1))

# Function to calculate total potential balance (current balance + sell value of all items)
def calculate_total_potential_balance():
    total = player_balance
    # Add sell price of anvil item if present
    if anvil_item:
        total += calculate_sell_price(anvil_item)
    # Add sell prices of inventory items
    for item in inventory_slots:
        if item:
            total += calculate_sell_price(item)
    return total

# Function to save game state
def save_game():
    global player_balance, inventory_slots, anvil_item
    save_data = {
        'player_balance': player_balance,
        'inventory_slots': [item.to_dict() if item else None for item in inventory_slots],
        'anvil_item': anvil_item.to_dict() if anvil_item else None,
        # No need to save 'inventory_slot_cost' as it can be recalculated
    }
    # Save with a timestamped filename
    filename = os.path.join(SAVE_DIR, f'save_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(filename, 'w') as f:
        json.dump(save_data, f)
    print(f"Game saved to {filename}")

# Function to load game state
def load_game(filename):
    global player_balance, inventory_slots, anvil_item, inventory_slot_cost
    with open(os.path.join(SAVE_DIR, filename), 'r') as f:
        save_data = json.load(f)
    player_balance = save_data['player_balance']
    inventory_slots = [Item.from_dict(item) if item else None for item in save_data['inventory_slots']]
    anvil_item = Item.from_dict(save_data['anvil_item']) if save_data['anvil_item'] else None
    # Recalculate 'inventory_slot_cost' based on number of inventory slots
    inventory_slot_cost = 5000 * 2 ** (len(inventory_slots) - 5)
    shop_inventory['slot']['price'] = inventory_slot_cost
    print(f"Game loaded from {filename}")

# Function to draw the main menu
def draw_main_menu():
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

# Function to draw the save files menu
def draw_save_files_menu(files):
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

# Main game loop
def main():
    global player_balance, dragging_item, drag_offset, anvil_item, game_over, inventory_slots, inventory_slot_cost
    global in_main_menu, in_game_menu, in_load_menu, menu_buttons, save_files, dragging_full_size_image

    clock = pygame.time.Clock()
    running = True

    # Main menu buttons
    menu_buttons = draw_main_menu()

    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if in_main_menu or in_game_menu or in_load_menu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if in_load_menu:
                        # Handle save file selection
                        buttons = draw_save_files_menu(save_files)
                        for filename, button_rect in buttons:
                            if button_rect.collidepoint(mouse_pos):
                                if filename == "Back":
                                    # Go back to previous menu
                                    in_load_menu = False
                                    if in_main_menu:
                                        menu_buttons = draw_main_menu()
                                    elif in_game_menu:
                                        menu_buttons = draw_main_menu()
                                else:
                                    # Load selected game
                                    load_game(filename)
                                    save_files = []
                                    in_main_menu = False
                                    in_game_menu = False
                                    in_load_menu = False
                                break
                    else:
                        # Handle menu button clicks
                        for option, button_rect in menu_buttons:
                            if button_rect.collidepoint(mouse_pos):
                                if option == "New Game":
                                    # Start new game
                                    player_balance = 5000
                                    inventory_slots = [None] * initial_inventory_slots
                                    # Calculate initial slot cost
                                    inventory_slot_cost = 5000 * 2 ** (len(inventory_slots) - 5)
                                    shop_inventory['slot']['price'] = inventory_slot_cost
                                    anvil_item = None
                                    game_over = False
                                    in_main_menu = False
                                    in_game_menu = False
                                    in_load_menu = False
                                elif option == "Save":
                                    # Save game
                                    save_game()
                                    in_game_menu = False
                                    in_load_menu = False
                                elif option == "Load":
                                    # Load game
                                    save_files = os.listdir(SAVE_DIR)
                                    save_files = [f for f in save_files if f.endswith('.json')]
                                    # Sort save files by date (most recent first)
                                    save_files.sort(reverse=True)
                                    in_load_menu = True
                                elif option == "Exit":
                                    # Exit game
                                    running = False
                                    break
                                elif option == "Return":
                                    # Return to game
                                    in_game_menu = False
                                    in_load_menu = False
                                break
                else:
                    # Redraw menu
                    if in_load_menu:
                        buttons = draw_save_files_menu(save_files)
                    else:
                        menu_buttons = draw_main_menu()
            elif game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if restart_button_rect.collidepoint(mouse_pos):
                        # Reset game state
                        player_balance = 5000
                        inventory_slots = [None] * initial_inventory_slots
                        # Calculate initial slot cost
                        inventory_slot_cost = 5000 * 2 ** (len(inventory_slots) - 5)
                        shop_inventory['slot']['price'] = inventory_slot_cost
                        anvil_item = None
                        game_over = False
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if Menu button is clicked
                    menu_button_rect = pygame.Rect(WIDTH - 100, 20, 80, 40)
                    if menu_button_rect.collidepoint(mouse_pos):
                        in_game_menu = True
                        menu_buttons = draw_main_menu()
                    else:
                        # Check shop items
                        for idx, (item_name, item_info) in enumerate(shop_inventory.items()):
                            item_rect = pygame.Rect(150, 50 + idx * 80, 50, 50)
                            if item_rect.collidepoint(mouse_pos):
                                if player_balance >= item_info['price']:
                                    if item_name == 'slot':
                                        # Purchase inventory slot
                                        if len(inventory_slots) < max_inventory_slots:
                                            player_balance -= item_info['price']
                                            inventory_slots.append(None)
                                            # Update slot price based on new number of slots
                                            inventory_slot_cost = 5000 * 2 ** (len(inventory_slots) - 5)
                                            shop_inventory['slot']['price'] = inventory_slot_cost
                                            # Check for game over
                                            if calculate_total_potential_balance() < 1000:
                                                game_over = True
                                        else:
                                            print("Maximum inventory slots reached.")
                                    else:
                                        player_balance -= item_info['price']
                                        dragging_item = Item(item_name, item_info['image'])
                                        drag_offset = (mouse_pos[0] - item_rect.x, mouse_pos[1] - item_rect.y)
                                        dragging_full_size_image = True
                                        # Check for game over
                                        if calculate_total_potential_balance() < 1000:
                                            game_over = True
                                else:
                                    # Not enough gold to purchase
                                    print("Not enough gold to purchase.")
                                break

                        # Check inventory slots
                        for idx, slot in enumerate(inventory_slots):
                            slot_x_start = (WIDTH - (min(10, len(inventory_slots)) * 60 - 10)) // 2
                            slot_x = slot_x_start + (idx % 10) * 60
                            slot_y_inv = HEIGHT - 70 - (idx // 10) * 60
                            slot_rect = pygame.Rect(slot_x, slot_y_inv, 50, 50)
                            if slot_rect.collidepoint(mouse_pos) and inventory_slots[idx]:
                                dragging_item = inventory_slots[idx]
                                inventory_slots[idx] = None
                                drag_offset = (mouse_pos[0] - slot_rect.x, mouse_pos[1] - slot_rect.y)
                                dragging_full_size_image = True
                                break

                        # Check anvil slot
                        slot_rect = pygame.Rect(slot_x_item, slot_y, 50, 50)
                        if slot_rect.collidepoint(mouse_pos) and anvil_item:
                            dragging_item = anvil_item
                            anvil_item = None
                            drag_offset = (mouse_pos[0] - slot_rect.x, mouse_pos[1] - slot_rect.y)
                            dragging_full_size_image = True

                        # Check upgrade button
                        if upgrade_button_rect.collidepoint(mouse_pos):
                            if anvil_item and anvil_item.name == 'sword':
                                if player_balance >= ITEM_PRICES['upgrade_kit']:
                                    player_balance -= ITEM_PRICES['upgrade_kit']
                                    success = random.random() < 0.65
                                    if success:
                                        anvil_item.level += 1
                                    else:
                                        anvil_item.level = 1
                                    # Check for game over
                                    if calculate_total_potential_balance() < 1000:
                                        game_over = True
                                else:
                                    # Not enough balance to pay for upgrade kit
                                    print("Not enough gold to upgrade.")

                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging_item:
                        mouse_pos = pygame.mouse.get_pos()
                        placed = False

                        # Place on anvil
                        slot_rect = pygame.Rect(slot_x_item, slot_y, 50, 50)
                        if slot_rect.collidepoint(mouse_pos) and not anvil_item:
                            if dragging_item.name == 'sword':
                                anvil_item = dragging_item
                                placed = True

                        # Place in inventory
                        if not placed:
                            for idx, slot in enumerate(inventory_slots):
                                slot_x_start = (WIDTH - (min(10, len(inventory_slots)) * 60 - 10)) // 2
                                slot_x = slot_x_start + (idx % 10) * 60
                                slot_y_inv = HEIGHT - 70 - (idx // 10) * 60
                                slot_rect = pygame.Rect(slot_x, slot_y_inv, 50, 50)
                                if slot_rect.collidepoint(mouse_pos) and not inventory_slots[idx]:
                                    inventory_slots[idx] = dragging_item
                                    placed = True
                                    break

                        # Sell to shop
                        if not placed:
                            shop_rect = pygame.Rect(100, 50, 150, 240)
                            if shop_rect.collidepoint(mouse_pos):
                                if dragging_item.name != 'slot':
                                    sell_price = calculate_sell_price(dragging_item)
                                    player_balance += sell_price
                                    placed = True

                        # If not placed, automatically move to free inventory slot
                        if not placed:
                            for idx, slot in enumerate(inventory_slots):
                                if not inventory_slots[idx]:
                                    inventory_slots[idx] = dragging_item
                                    placed = True
                                    break

                        # If still not placed, discard item (inventory full)
                        if not placed:
                            # Optionally, display a message that the inventory is full
                            print("Inventory is full! Item discarded.")

                        dragging_item = None
                        dragging_full_size_image = False

        # Drawing
        if in_main_menu or in_game_menu or in_load_menu:
            if in_load_menu:
                buttons = draw_save_files_menu(save_files)
            else:
                menu_buttons = draw_main_menu()
        elif game_over:
            # Draw game over screen
            game_over_text = large_font.render("Smithy went bankrupt!!!", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))

            pygame.draw.rect(screen, RED, restart_button_rect)
            restart_text = font.render("Start again", True, WHITE)
            screen.blit(restart_text, (restart_button_rect.x + (restart_button_rect.width - restart_text.get_width()) // 2,
                                       restart_button_rect.y + (restart_button_rect.height - restart_text.get_height()) // 2))
        else:
            # Draw game elements
            # Draw shop
            shop_text = font.render("Shop", True, WHITE)
            screen.blit(shop_text, (100, 20))
            for idx, (item_name, item_info) in enumerate(shop_inventory.items()):
                item_rect = pygame.Rect(150, 50 + idx * 80, 50, 50)
                pygame.draw.rect(screen, WHITE, item_rect, 2)
                # Draw item name to the left of the icon
                name_text = font.render(item_name.capitalize(), True, WHITE)
                screen.blit(name_text, (item_rect.x - name_text.get_width() - 10, item_rect.y + 15))
                if item_info['image']:
                    item_image = pygame.transform.scale(item_info['image'], (50, 50))
                    screen.blit(item_image, item_rect.topleft)
                else:
                    # For inventory slot purchase, draw a placeholder
                    slot_icon = pygame.Surface((50, 50))
                    slot_icon.fill(GRAY)
                    screen.blit(slot_icon, item_rect.topleft)
                price_text = font.render(f"{item_info['price']}g", True, WHITE)
                screen.blit(price_text, (item_rect.x, item_rect.y + 55))

            # Draw anvil
            screen.blit(anvil_img, anvil_pos)
            # Draw anvil slot
            slot_rect = pygame.Rect(slot_x_item, slot_y, 50, 50)
            pygame.draw.rect(screen, WHITE, slot_rect, 2)
            if anvil_item:
                anvil_item.draw(screen, slot_rect.topleft)

            # Draw upgrade button
            if anvil_item:
                pygame.draw.rect(screen, (0, 200, 0), upgrade_button_rect)
            else:
                pygame.draw.rect(screen, (100, 100, 100), upgrade_button_rect)
            upgrade_text = font.render("Upgrade", True, WHITE)
            screen.blit(upgrade_text, (upgrade_button_rect.x + 5, upgrade_button_rect.y + 10))

            # Draw inventory
            # Calculate starting x position to center the inventory slots
            num_slots_in_row = min(10, len(inventory_slots))
            total_slots_width = num_slots_in_row * 60 - 10
            slot_x_start = (WIDTH - total_slots_width) // 2

            # Draw "Inventory" label to the left of the inventory slots
            inventory_text = font.render("Inventory", True, WHITE)
            inventory_text_x = slot_x_start - inventory_text.get_width() - 20
            inventory_text_y = HEIGHT - 70 - ((len(inventory_slots) - 1) // 10) * 60 + 15
            screen.blit(inventory_text, (inventory_text_x, inventory_text_y))

            for idx, slot in enumerate(inventory_slots):
                slot_x = slot_x_start + (idx % 10) * 60
                slot_y_inv = HEIGHT - 70 - (idx // 10) * 60
                slot_rect = pygame.Rect(slot_x, slot_y_inv, 50, 50)
                pygame.draw.rect(screen, WHITE, slot_rect, 2)
                if slot:
                    slot.draw(screen, slot_rect.topleft)

            # Draw balance at bottom-right corner
            balance_text = font.render(f"Balance: {player_balance}g", True, WHITE)
            balance_text_rect = balance_text.get_rect()
            balance_text_pos = (WIDTH - balance_text_rect.width - 20, HEIGHT - balance_text_rect.height - 20)
            screen.blit(balance_text, balance_text_pos)

            # Draw Menu button
            menu_button_rect = pygame.Rect(WIDTH - 100, 20, 80, 40)
            pygame.draw.rect(screen, GRAY, menu_button_rect)
            menu_text = font.render("Menu", True, WHITE)
            screen.blit(menu_text, (menu_button_rect.x + (menu_button_rect.width - menu_text.get_width()) // 2,
                                    menu_button_rect.y + (menu_button_rect.height - menu_text.get_height()) // 2))

            # Draw dragging item
            if dragging_item:
                mouse_pos = pygame.mouse.get_pos()
                if dragging_full_size_image:
                    dragging_item.draw(screen, (mouse_pos[0] - drag_offset[0], mouse_pos[1] - drag_offset[1]), dragging=True)
                else:
                    dragging_item.draw(screen, (mouse_pos[0] - drag_offset[0], mouse_pos[1] - drag_offset[1]))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()