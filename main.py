import pygame
import sys
import os
import random
import json

from constants import *
from items import Item, calculate_sell_price
from notifications import notifications, add_notification
from menus import draw_main_menu, draw_save_files_menu, draw_save_menu, save_game, load_game
from utils import calculate_total_potential_balance

def main():
    # Инициализация глобальных переменных игры
    player_balance = 5000
    initial_inventory_slots = 5
    max_inventory_slots = 30
    inventory_slots = [None] * initial_inventory_slots  # Начинаем с 5 слотов
    inventory_slot_cost = 5000  # Начальная стоимость дополнительного слота

    # Инвентарь магазина
    shop_inventory = {
        'sword': {'image': sword_img_full, 'price': ITEM_PRICES['sword']},
        'slot': {'image': None, 'price': inventory_slot_cost},  # Покупка слота
    }

    anvil_item = None  # Слот на наковальне

    # Позиции
    anvil_pos = (WIDTH // 2 - anvil_img.get_width() // 2, HEIGHT // 2 - anvil_img.get_height() // 2 - 50)
    upgrade_button_rect = pygame.Rect(WIDTH // 2 - 40, anvil_pos[1] + anvil_img.get_height() + 80, 80, 40)
    # Позиция слота (по центру под наковальней)
    slot_y = anvil_pos[1] + anvil_img.get_height() + 10
    slot_x_item = WIDTH // 2 - 25  # Центрируем слот

    # Переменные состояния игры
    in_main_menu = True
    in_game_menu = False
    in_load_menu = False
    in_save_menu = False
    game_over = False

    # Переменные меню сохранения
    save_name_input = ''
    overwrite_confirm = False

    menu_buttons = []
    save_files = []
    dragging_item = None
    drag_offset = (0, 0)
    dragging_full_size_image = None

    clock = pygame.time.Clock()
    running = True

    # Кнопки главного меню
    menu_buttons = draw_main_menu(screen, in_main_menu)

    while running:
        dt = clock.tick(60) / 1000  # Количество секунд между каждым циклом
        screen.fill(BLACK)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if overwrite_confirm:
                # Обработка событий для диалога подтверждения перезаписи
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if yes_button_rect.collidepoint(mouse_pos):
                        # Пользователь подтверждает перезапись
                        save_game(player_balance, inventory_slots, anvil_item, save_name_input)
                        in_save_menu = False
                        overwrite_confirm = False
                        save_name_input = ''
                    elif no_button_rect.collidepoint(mouse_pos):
                        # Отмена перезаписи
                        overwrite_confirm = False
                # Игнорируем остальные события
                continue

            if in_main_menu or in_game_menu or in_load_menu or in_save_menu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if in_load_menu:
                        # Обработка выбора файла сохранения
                        buttons = draw_save_files_menu(screen, save_files)
                        for filename, button_rect in buttons:
                            if button_rect.collidepoint(mouse_pos):
                                if filename == "Back":
                                    # Возвращаемся в предыдущее меню
                                    in_load_menu = False
                                    if in_main_menu:
                                        menu_buttons = draw_main_menu(screen, in_main_menu)
                                    elif in_game_menu:
                                        menu_buttons = draw_main_menu(screen, in_main_menu=False)
                                else:
                                    # Загружаем выбранное сохранение
                                    save_data = load_game(filename)
                                    # Загружаем данные игры
                                    player_balance = save_data['player_balance']
                                    inventory_slots = [Item.from_dict(item) if item else None for item in save_data['inventory_slots']]
                                    anvil_item = Item.from_dict(save_data['anvil_item']) if save_data['anvil_item'] else None
                                    # Пересчитываем стоимость слота на основе количества слотов
                                    inventory_slot_cost = 5000 * 2 ** (len(inventory_slots) - 5)
                                    shop_inventory['slot']['price'] = inventory_slot_cost
                                    save_files = []
                                    in_main_menu = False
                                    in_game_menu = False
                                    in_load_menu = False
                                break
                    elif in_save_menu:
                        # Обработка взаимодействия в меню сохранения
                        input_rect, buttons, save_button_rect, back_button_rect = draw_save_menu(screen, save_name_input, save_files)
                        if back_button_rect.collidepoint(mouse_pos):
                            # Возвращаемся в предыдущее меню
                            in_save_menu = False
                            overwrite_confirm = False
                            save_name_input = ''
                            if in_game_menu:
                                menu_buttons = draw_main_menu(screen, in_main_menu=False)
                            elif in_main_menu:
                                menu_buttons = draw_main_menu(screen, in_main_menu)
                        elif save_button_rect.collidepoint(mouse_pos):
                            if save_name_input.strip() == '':
                                add_notification("Please enter a save name.")
                            else:
                                filename = f"{save_name_input}.json"
                                filepath = os.path.join(SAVE_DIR, filename)
                                if os.path.exists(filepath):
                                    overwrite_confirm = True
                                else:
                                    # Сохраняем игру
                                    save_game(player_balance, inventory_slots, anvil_item, save_name_input)
                                    in_save_menu = False
                                    overwrite_confirm = False
                                    save_name_input = ''
                        else:
                            # Проверяем, кликнул ли пользователь по существующему сохранению
                            for filename, button_rect in buttons:
                                if button_rect.collidepoint(mouse_pos):
                                    save_name_input = filename[:-5]  # Убираем '.json'
                                    break
                    else:
                        # Обработка нажатий на кнопки меню
                        for option, button_rect in menu_buttons:
                            if button_rect.collidepoint(mouse_pos):
                                if option == "New Game":
                                    # Начинаем новую игру
                                    player_balance = 5000
                                    inventory_slots = [None] * initial_inventory_slots
                                    # Пересчитываем стоимость слота
                                    inventory_slot_cost = 5000 * 2 ** (len(inventory_slots) - 5)
                                    shop_inventory['slot']['price'] = inventory_slot_cost
                                    anvil_item = None
                                    game_over = False
                                    in_main_menu = False
                                    in_game_menu = False
                                    in_load_menu = False
                                    in_save_menu = False
                                    notifications.clear()
                                elif option == "Save":
                                    # Открываем меню сохранения
                                    save_files = os.listdir(SAVE_DIR)
                                    save_files = [f for f in save_files if f.endswith('.json')]
                                    save_name_input = ''
                                    in_save_menu = True
                                    overwrite_confirm = False
                                elif option == "Load":
                                    # Загружаем игру
                                    save_files = os.listdir(SAVE_DIR)
                                    save_files = [f for f in save_files if f.endswith('.json')]
                                    # Сортируем сохранения по алфавиту
                                    save_files.sort()
                                    in_load_menu = True
                                elif option == "Exit":
                                    # Выходим из игры
                                    running = False
                                    break
                                elif option == "Return":
                                    # Возвращаемся в игру
                                    in_game_menu = False
                                    in_load_menu = False
                                    in_save_menu = False
                                break
                elif event.type == pygame.KEYDOWN:
                    if in_save_menu and not overwrite_confirm:
                        if event.key == pygame.K_BACKSPACE:
                            save_name_input = save_name_input[:-1]
                        elif event.key == pygame.K_RETURN:
                            if save_name_input.strip() == '':
                                add_notification("Please enter a save name.")
                            else:
                                filename = f"{save_name_input}.json"
                                filepath = os.path.join(SAVE_DIR, filename)
                                if os.path.exists(filepath):
                                    overwrite_confirm = True
                                else:
                                    # Сохраняем игру
                                    save_game(player_balance, inventory_slots, anvil_item, save_name_input)
                                    in_save_menu = False
                                    overwrite_confirm = False
                                    save_name_input = ''
                        else:
                            save_name_input += event.unicode
            elif game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    restart_button_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 30, 120, 40)
                    if restart_button_rect.collidepoint(mouse_pos):
                        # Сбрасываем состояние игры
                        player_balance = 5000
                        inventory_slots = [None] * initial_inventory_slots
                        # Пересчитываем стоимость слота
                        inventory_slot_cost = 5000 * 2 ** (len(inventory_slots) - 5)
                        shop_inventory['slot']['price'] = inventory_slot_cost
                        anvil_item = None
                        game_over = False
                        notifications.clear()
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Проверяем, нажата ли кнопка Меню
                    menu_button_rect = pygame.Rect(WIDTH - 100, 20, 80, 40)
                    if menu_button_rect.collidepoint(mouse_pos):
                        in_game_menu = True
                        menu_buttons = draw_main_menu(screen, in_main_menu=False)
                    else:
                        # Проверяем, нажата ли кнопка закрытия уведомления
                        for notification in notifications:
                            if notification.is_clicked(mouse_pos):
                                notifications.remove(notification)
                                break
                        else:
                            # Проверяем предметы в магазине
                            for idx, (item_name, item_info) in enumerate(shop_inventory.items()):
                                item_rect = pygame.Rect(150, 50 + idx * 80, 50, 50)
                                if item_rect.collidepoint(mouse_pos):
                                    if player_balance >= item_info['price']:
                                        if item_name == 'slot':
                                            # Покупаем слот инвентаря
                                            if len(inventory_slots) < max_inventory_slots:
                                                player_balance -= item_info['price']
                                                inventory_slots.append(None)
                                                # Обновляем цену слота
                                                inventory_slot_cost = 5000 * 2 ** (len(inventory_slots) - 5)
                                                shop_inventory['slot']['price'] = inventory_slot_cost
                                                # Проверяем на конец игры
                                                if calculate_total_potential_balance(player_balance, anvil_item, inventory_slots) < 1000:
                                                    game_over = True
                                            else:
                                                add_notification("Maximum inventory slots reached.")
                                        else:
                                            player_balance -= item_info['price']
                                            dragging_item = Item(item_name, item_info['image'])
                                            drag_offset = (mouse_pos[0] - item_rect.x, mouse_pos[1] - item_rect.y)
                                            dragging_full_size_image = True
                                            # Проверяем на конец игры
                                            if calculate_total_potential_balance(player_balance, anvil_item, inventory_slots) < 1000:
                                                game_over = True
                                    else:
                                        # Недостаточно золота
                                        add_notification("Not enough gold to purchase.")
                                    break
                            # Проверяем слоты инвентаря
                            for idx, slot in enumerate(inventory_slots):
                                num_slots_in_row = min(10, len(inventory_slots))
                                total_slots_width = num_slots_in_row * 60 - 10
                                slot_x_start = (WIDTH - total_slots_width) // 2
                                slot_x = slot_x_start + (idx % 10) * 60
                                slot_y_inv = HEIGHT - 70 - (idx // 10) * 60
                                slot_rect = pygame.Rect(slot_x, slot_y_inv, 50, 50)
                                if slot_rect.collidepoint(mouse_pos) and inventory_slots[idx]:
                                    dragging_item = inventory_slots[idx]
                                    inventory_slots[idx] = None
                                    drag_offset = (mouse_pos[0] - slot_rect.x, mouse_pos[1] - slot_rect.y)
                                    dragging_full_size_image = True
                                    break
                            # Проверяем слот на наковальне
                            slot_rect = pygame.Rect(slot_x_item, slot_y, 50, 50)
                            if slot_rect.collidepoint(mouse_pos) and anvil_item:
                                dragging_item = anvil_item
                                anvil_item = None
                                drag_offset = (mouse_pos[0] - slot_rect.x, mouse_pos[1] - slot_rect.y)
                                dragging_full_size_image = True
                            # Проверяем кнопку улучшения
                            if upgrade_button_rect.collidepoint(mouse_pos):
                                if anvil_item and anvil_item.name == 'sword':
                                    if player_balance >= ITEM_PRICES['upgrade_kit']:
                                        player_balance -= ITEM_PRICES['upgrade_kit']
                                        success = random.random() < 0.65
                                        if success:
                                            anvil_item.level += 1
                                            add_notification("Upgrade successful!")
                                        else:
                                            anvil_item.level = 1
                                            add_notification("Upgrade failed. Item reset to Level 1.")
                                        # Проверяем на конец игры
                                        if calculate_total_potential_balance(player_balance, anvil_item, inventory_slots) < 1000:
                                            game_over = True
                                    else:
                                        # Недостаточно золота
                                        add_notification("Not enough gold to upgrade.")
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging_item:
                        mouse_pos = pygame.mouse.get_pos()
                        placed = False
                        # Помещаем на наковальню
                        slot_rect = pygame.Rect(slot_x_item, slot_y, 50, 50)
                        if slot_rect.collidepoint(mouse_pos) and not anvil_item:
                            if dragging_item.name == 'sword':
                                anvil_item = dragging_item
                                placed = True
                        # Помещаем в инвентарь
                        if not placed:
                            for idx, slot in enumerate(inventory_slots):
                                num_slots_in_row = min(10, len(inventory_slots))
                                total_slots_width = num_slots_in_row * 60 - 10
                                slot_x_start = (WIDTH - total_slots_width) // 2
                                slot_x = slot_x_start + (idx % 10) * 60
                                slot_y_inv = HEIGHT - 70 - (idx // 10) * 60
                                slot_rect = pygame.Rect(slot_x, slot_y_inv, 50, 50)
                                if slot_rect.collidepoint(mouse_pos) and not inventory_slots[idx]:
                                    inventory_slots[idx] = dragging_item
                                    placed = True
                                    break
                        # Продаем в магазин
                        if not placed:
                            shop_rect = pygame.Rect(100, 50, 150, 240)
                            if shop_rect.collidepoint(mouse_pos):
                                if dragging_item.name != 'slot':
                                    sell_price = calculate_sell_price(dragging_item)
                                    player_balance += sell_price
                                    add_notification(f"Sold item for {sell_price}g.")
                                    placed = True
                        # Если не удалось разместить, пытаемся поместить в свободный слот инвентаря
                        if not placed:
                            for idx, slot in enumerate(inventory_slots):
                                if not inventory_slots[idx]:
                                    inventory_slots[idx] = dragging_item
                                    placed = True
                                    break
                        # Если инвентарь полон, предмет пропадает
                        if not placed:
                            add_notification("Inventory is full! Item discarded.")
                        dragging_item = None
                        dragging_full_size_image = False

        # Отрисовка
        if in_main_menu or in_game_menu or in_load_menu or in_save_menu:
            if in_load_menu:
                buttons = draw_save_files_menu(screen, save_files)
            elif in_save_menu:
                input_rect, buttons, save_button_rect, back_button_rect = draw_save_menu(screen, save_name_input, save_files)
            else:
                menu_buttons = draw_main_menu(screen, in_main_menu=in_main_menu)
        elif game_over:
            # Отрисовка экрана окончания игры
            game_over_text = large_font.render("Smithy went bankrupt!!!", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))

            restart_button_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 30, 120, 40)
            pygame.draw.rect(screen, RED, restart_button_rect)
            restart_text = font.render("Start again", True, WHITE)
            screen.blit(restart_text, (restart_button_rect.x + (restart_button_rect.width - restart_text.get_width()) // 2,
                                       restart_button_rect.y + (restart_button_rect.height - restart_text.get_height()) // 2))
        else:
            # Отрисовка элементов игры
            # Отрисовка магазина
            shop_text = font.render("Shop", True, WHITE)
            screen.blit(shop_text, (100, 20))
            for idx, (item_name, item_info) in enumerate(shop_inventory.items()):
                item_rect = pygame.Rect(150, 50 + idx * 80, 50, 50)
                pygame.draw.rect(screen, WHITE, item_rect, 2)
                # Отрисовка названия предмета
                name_text = font.render(item_name.capitalize(), True, WHITE)
                screen.blit(name_text, (item_rect.x - name_text.get_width() - 10, item_rect.y + 15))
                if item_info['image']:
                    item_image = pygame.transform.scale(item_info['image'], (50, 50))
                    screen.blit(item_image, item_rect.topleft)
                else:
                    # Для покупки слота рисуем заглушку
                    slot_icon = pygame.Surface((50, 50))
                    slot_icon.fill(GRAY)
                    screen.blit(slot_icon, item_rect.topleft)
                price_text = font.render(f"{item_info['price']}g", True, WHITE)
                screen.blit(price_text, (item_rect.x, item_rect.y + 55))
            # Отрисовка наковальни
            screen.blit(anvil_img, anvil_pos)
            # Отрисовка слота на наковальне
            slot_rect = pygame.Rect(slot_x_item, slot_y, 50, 50)
            pygame.draw.rect(screen, WHITE, slot_rect, 2)
            if anvil_item:
                anvil_item.draw(screen, slot_rect.topleft)
            # Отрисовка кнопки улучшения
            if anvil_item:
                pygame.draw.rect(screen, (0, 200, 0), upgrade_button_rect)
            else:
                pygame.draw.rect(screen, (100, 100, 100), upgrade_button_rect)
            upgrade_text = font.render("Upgrade", True, WHITE)
            screen.blit(upgrade_text, (upgrade_button_rect.x + 5, upgrade_button_rect.y + 10))
            # Отрисовка инвентаря
            num_slots_in_row = min(10, len(inventory_slots))
            total_slots_width = num_slots_in_row * 60 - 10
            slot_x_start = (WIDTH - total_slots_width) // 2
            # Отрисовка надписи "Inventory"
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
            # Отрисовка баланса
            balance_text = font.render(f"Balance: {player_balance}g", True, WHITE)
            balance_text_rect = balance_text.get_rect()
            balance_text_pos = (WIDTH - balance_text_rect.width - 20, HEIGHT - balance_text_rect.height - 20)
            screen.blit(balance_text, balance_text_pos)
            # Отрисовка кнопки Меню
            menu_button_rect = pygame.Rect(WIDTH - 100, 20, 80, 40)
            pygame.draw.rect(screen, GRAY, menu_button_rect)
            menu_text = font.render("Menu", True, WHITE)
            screen.blit(menu_text, (menu_button_rect.x + (menu_button_rect.width - menu_text.get_width()) // 2,
                                    menu_button_rect.y + (menu_button_rect.height - menu_text.get_height()) // 2))
            # Отрисовка перетаскиваемого предмета
            if dragging_item:
                mouse_pos = pygame.mouse.get_pos()
                if dragging_full_size_image:
                    dragging_item.draw(screen, (mouse_pos[0] - drag_offset[0], mouse_pos[1] - drag_offset[1]), dragging=True)
                else:
                    dragging_item.draw(screen, (mouse_pos[0] - drag_offset[0], mouse_pos[1] - drag_offset[1]))

        # Если активен диалог подтверждения перезаписи, отрисовываем его поверх
        if overwrite_confirm:
            # Определяем прямоугольники здесь, чтобы они были доступны при отрисовке и обработке событий
            confirm_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
            yes_button_rect = pygame.Rect(confirm_rect.x + 50, confirm_rect.y + 120, 100, 40)
            no_button_rect = pygame.Rect(confirm_rect.x + 250, confirm_rect.y + 120, 100, 40)
            # Отрисовка полупрозрачного фона
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            # Отрисовка диалога подтверждения
            pygame.draw.rect(screen, DARK_GRAY, confirm_rect)
            confirm_text = font.render(f"Overwrite existing save '{save_name_input}'?", True, WHITE)
            screen.blit(confirm_text, (confirm_rect.x + 20, confirm_rect.y + 50))
            # Отрисовка кнопок Да и Нет
            pygame.draw.rect(screen, GRAY, yes_button_rect)
            pygame.draw.rect(screen, GRAY, no_button_rect)
            yes_text = font.render("Yes", True, WHITE)
            no_text = font.render("No", True, WHITE)
            screen.blit(yes_text, (yes_button_rect.x + (yes_button_rect.width - yes_text.get_width()) // 2,
                                   yes_button_rect.y + (yes_button_rect.height - yes_text.get_height()) // 2))
            screen.blit(no_text, (no_button_rect.x + (no_button_rect.width - no_text.get_width()) // 2,
                                  no_button_rect.y + (no_button_rect.height - no_text.get_height()) // 2))

        # Обновление и отрисовка уведомлений
        for notification in notifications[:]:
            if not notification.update(dt):
                notifications.remove(notification)
            else:
                notification.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()