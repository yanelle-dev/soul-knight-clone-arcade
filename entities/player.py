import arcade
import math
import config
import database
from entities.entity import Entity
from weapons.weapons import Blaster, Sword


class Player(Entity):
    def __init__(self, x, y):
        default_skin_path = config.SKINS_CONFIG[0]["image"]
        # Загружаем текстуру персонажа
        try:
            import os
            if os.path.exists(default_skin_path):
                super().__init__(default_skin_path, config.PLAYER_SCALE, x, y)
            else:
                super().__init__(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", 
                               config.SPRITE_SCALING, x, y)
        except Exception:
            super().__init__(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", 
                           config.SPRITE_SCALING, x, y)

        self.speed = config.PLAYER_SPEED
        self.max_hp = config.PLAYER_MAX_HP
        self.hp = self.max_hp
        self.armor = 0

        self.crystals = database.get_crystals()
        self.score = 0

        # Спрайт оружия (масштаб в руках задаём в update через scale_x/scale_y)
        self.weapon_sprite = arcade.Sprite(scale=1.0)
        self.weapon_list = arcade.SpriteList()
        self.weapon_list.append(self.weapon_sprite)

        self.mouse_angle = 0

        self.weapon = Sword()
        self.equip_weapon_visuals("Sword")

        self.current_skin_name = config.SKINS_CONFIG[0]["name"]

        # Направление взгляда (False = вправо, True = влево)
        self.facing_left = False

    def update_crystals_from_db(self):
        self.crystals = database.get_crystals()

    def equip_skin(self, skin_name):
        for skin_data in config.SKINS_CONFIG:
            if skin_data["name"] == skin_name:
                try:
                    self.texture = arcade.load_texture(skin_data["image"])
                    self.current_skin_name = skin_name
                except Exception as e:
                    print(f"Ошибка загрузки текстуры {skin_data['image']}: {e}")
                    # Используем стандартную текстуру при ошибке
                    self.texture = arcade.load_texture(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png")
                break

    def equip_weapon_visuals(self, weapon_name):
        for w_data in config.WEAPONS_CONFIG:
            if w_data["class_name"] == weapon_name:
                # Загружаем текстуру. mech.png должен быть рядом с main.py
                self.weapon_sprite.texture = arcade.load_texture(w_data["image"])
                return

    def equip_weapon_by_name(self, class_name):
        if class_name == "Blaster":
            self.weapon = Blaster()
        elif class_name == "Sword":
            self.weapon = Sword()

        self.equip_weapon_visuals(class_name)

    def take_damage(self, amount):
        if self.armor > 0:
            if self.armor >= amount:
                self.armor -= amount
                return
            else:
                amount -= self.armor
                self.armor = 0
        self.hp -= amount

    def update(self, delta_time: float = 1 / 60):
        if hasattr(self.weapon, 'update'):
            self.weapon.update(delta_time)

        # Определяем направление движения игрока
        if self.change_x < 0:
            self.facing_left = True
        elif self.change_x > 0:
            self.facing_left = False

        # Применяем масштаб и зеркалирование для самого персонажа
        player_scale = getattr(config, 'PLAYER_SCALE', 1.0)
        self.scale_y = player_scale
        if self.facing_left:
            self.scale_x = -player_scale  # Отрицательный scale_x зеркалит персонажа влево
        else:
            self.scale_x = player_scale   # Положительный scale_x оставляет стандартный вид (вправо)

        # Расстояние от игрока до оружия
        distance = 25

        # Проверяем тип оружия для правильного позиционирования и масштаба
        is_blaster = isinstance(self.weapon, Blaster)
        if is_blaster:
            base_scale = config.BLASTER_IN_HAND_SCALE
        else:
            base_scale = config.SWORD_IN_HAND_SCALE

        if self.facing_left:
            # Смотрим влево
            self.weapon_sprite.center_x = self.center_x - distance
            if is_blaster:
                # Бластер: левый конец к игроку, правый вверх и влево (как меч)
                # Отзеркаливаем бластер
                self.weapon_sprite.scale_x = -base_scale
                self.weapon_sprite.scale_y = base_scale
                self.weapon_sprite.angle = 45  # Поворот вверх и влево
            else:
                # Меч
                self.weapon_sprite.scale_x = base_scale
                self.weapon_sprite.scale_y = base_scale
                self.weapon_sprite.angle = 0
        else:
            # Смотрим вправо
            self.weapon_sprite.center_x = self.center_x + distance
            if is_blaster:
                # Бластер: левый конец к игроку, правый вверх и вправо (зеркально)
                # Отзеркаливаем бластер
                self.weapon_sprite.scale_x = base_scale
                self.weapon_sprite.scale_y = base_scale
                self.weapon_sprite.angle = -45  # Поворот вверх и вправо
            else:
                # Меч (отзеркаливаем по X)
                self.weapon_sprite.scale_x = -base_scale
                self.weapon_sprite.scale_y = base_scale
                self.weapon_sprite.angle = 0

        # Чуть ниже центра игрока
        self.weapon_sprite.center_y = self.center_y - 10

        super().update(delta_time)