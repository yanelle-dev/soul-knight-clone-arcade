import arcade
import math
import random
import config
import database
from entities.entity import Entity

class Item(Entity):
    def __init__(self, filename, x, y, scale=config.SPRITE_SCALING):
        super().__init__(filename, scale, x, y)

    def on_pickup(self, player):
        return False

class WeaponDrop(Item):
    def __init__(self, x, y, weapon_class_name, texture_path):
        super().__init__(texture_path, x, y)
        self.weapon_name = weapon_class_name
        self.scale_change = 0.01

    def update(self, delta_time: float = 1/60):
        super().update(delta_time)
        current_scale = self.scale[0]
        new_scale = current_scale + self.scale_change
        self.scale = new_scale
        if new_scale > 1.2 * config.SPRITE_SCALING or new_scale < 0.8 * config.SPRITE_SCALING:
            self.scale_change *= -1

    def on_pickup(self, player):
        database.unlock_weapon(self.weapon_name)
        player.equip_weapon_by_name(self.weapon_name)
        return True

class Chest(Entity):
    def __init__(self, x, y):
        super().__init__("images/sunduk.png", config.SPRITE_SCALING * 0.7, x, y)
        self.color = (255, 255, 255)

    def open(self):
        rnd = random.random()
        if rnd < 0.4:
            return WeaponDrop(self.center_x, self.center_y, "Blaster", "images/blaster.png")
        elif rnd < 0.7:
            return HealthPotion(self.center_x, self.center_y)
        else:
            return ShieldItem(self.center_x, self.center_y)

class HealthPotion(Item):
    def __init__(self, x, y):
        super().__init__("images/aptechka.png", x, y)
        self.heal_amount = 20

    def on_pickup(self, player):
        if player.hp < player.max_hp:
            player.hp += self.heal_amount
            if player.hp > player.max_hp:
                player.hp = player.max_hp
            return True
        return False

class ShieldItem(Item):
    def __init__(self, x, y):
        super().__init__(":resources:images/items/gold_1.png", x, y)
        self.shield_amount = config.SHIELD_AMOUNT

    def on_pickup(self, player):
        if player.armor < config.PLAYER_MAX_ARMOR:
            player.armor += self.shield_amount
            if player.armor > config.PLAYER_MAX_ARMOR:
                player.armor = config.PLAYER_MAX_ARMOR
            return True
        return False

class CrystalDrop(Item):
    def __init__(self, x, y, amount=5):
        super().__init__(":resources:images/items/gemBlue.png", x, y)
        self.amount = amount
        self.scale_change = 0.01

    def update(self, delta_time: float = 1/60):
        super().update(delta_time)
        current_scale = self.scale[0]
        new_scale = current_scale + self.scale_change
        self.scale = new_scale
        if new_scale > 0.6 or new_scale < 0.4:
            self.scale_change *= -1

    def on_pickup(self, player):
        return True

# --- ПОРТАЛ (БЕЗ АНИМАЦИИ) ---
class Portal(Entity):
    def __init__(self, x, y):
        super().__init__("assets/portal.png", 0.5, x, y)

    def update(self, delta_time: float = 1/60):
        super().update(delta_time)
