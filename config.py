import arcade

# --- Настройки окна ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Soul Knight Clone (Arcade)"

# --- Настройки игры ---
# Общий масштаб спрайтов (стены, враги, предметы)
SPRITE_SCALING = 0.3
TILE_SCALING = 0.3
PLAYER_SPEED = 3.5
PLAYER_MAX_HP = 100
PLAYER_MAX_ARMOR = 50
BULLET_SPEED = 12

# --- Масштабы персонажа и оружия ---
# Масштаб ТОЛЬКО для игрока (персонажа)
PLAYER_SCALE = 0.07
# Базовый масштаб меча в руках
SWORD_IN_HAND_SCALE = 0.03
# Базовый масштаб бластера в руках (можно настраивать отдельно)
BLASTER_IN_HAND_SCALE = 0.07

# --- Настройки уровня ---
ROOM_WIDTH_PX = 1024
ROOM_HEIGHT_PX = 768

# --- Настройки врагов ---
ENEMY_SCALING = 0.5
ENEMY_SPEED = 2
ENEMY_HP = 30
ENEMY_DAMAGE = 10
ZOMBIE_HP = 30
ZOMBIE_SPEED = 2.0
ZOMBIE_DAMAGE = 10
ZOMBIE_IMAGE = ":resources:images/animated_characters/zombie/zombie_idle.png"
ROBOT_HP = 40
ROBOT_SPEED = 1.0
ROBOT_DAMAGE = 15
ROBOT_IMAGE = ":resources:images/animated_characters/robot/robot_idle.png"
ROBOT_ATTACK_RANGE = 300
ROBOT_COOLDOWN = 2.0
SLIME_HP = 80
SLIME_SPEED = 0.8
SLIME_DAMAGE = 20
SLIME_IMAGE = ":resources:images/enemies/slimeBlock.png"
BAT_HP = 15
BAT_SPEED = 4.0
BAT_DAMAGE = 5
BAT_IMAGE = ":resources:images/enemies/fly.png"

# --- Цвета ---
BG_COLOR = arcade.color.BLACK

# --- Настройки UI ---
UI_FONT_SIZE = 20
UI_BAR_WIDTH = 200
UI_BAR_HEIGHT = 20
UI_HEALTH_COLOR = arcade.color.RED
UI_BG_COLOR = arcade.color.DARK_GRAY

# --- Пути ---
# Папка с пользовательскими изображениями
ASSET_PATH = "assets/"

# --- ПРЕДМЕТЫ ---
CHEST_PROBABILITY = 1.0
SHIELD_AMOUNT = 25

# --- СПИСОК СКИНОВ ---
# image  – большая картинка для персонажа в игре
# icon   – маленькая иконка для меню (чтобы не раздувать фон, как на скрине)
SKINS_CONFIG = [
    {
        "name": "Adventurer",
        "price": 0,
        "image": "assets/pers.png",
        "icon": ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
    },
    {
        "name": "Knight",
        "price": 50,
        "image": ":resources:images/animated_characters/male_person/malePerson_idle.png"
    },
    {
        "name": "Robot",
        "price": 100,
        "image": ":resources:images/animated_characters/robot/robot_idle.png"
    },
    {
        "name": "Zombie",
        "price": 200,
        "image": ":resources:images/animated_characters/zombie/zombie_idle.png"
    }
]

# --- ОРУЖИЕ ---
WEAPONS_CONFIG = [
    {
        "name": "Sword",
        "price": 0,
        "class_name": "Sword",
        "image": "assets/mech.png",  # ВАША КАРТИНКА
        "damage": 15,
        "cooldown": 0.4,
        "type": "melee"
    },
    {
        "name": "Blaster",
        "price": 200,
        "class_name": "Blaster",
        "image": "assets/blaster.png",  # ВАША КАРТИНКА
        "damage": 5,
        "cooldown": 0.1,
        "type": "ranged"
    }
]