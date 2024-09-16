import math
from constants import ITEM_PRICES

def calculate_total_potential_balance(player_balance, anvil_item, inventory_slots):
    total = player_balance
    # Add sell price of anvil item if present
    if anvil_item:
        total += calculate_sell_price(anvil_item)
    # Add sell prices of inventory items
    for item in inventory_slots:
        if item:
            total += calculate_sell_price(item)
    return total

def calculate_sell_price(item):
    base_price = ITEM_PRICES[item.name]
    return int(base_price * math.exp(item.level - 1))