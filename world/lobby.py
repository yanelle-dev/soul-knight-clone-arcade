import arcade
import config
from world.tiles import Wall, Floor
from entities.interactables import Portal, SkinChanger, WeaponStand


class Lobby:
    def __init__(self):
        self.wall_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.interactable_list = arcade.SpriteList()
        self.decor_list = arcade.SpriteList()

        # Список для текста над объектами
        self.texts = []

    def setup(self):
        self.wall_list.clear()
        self.floor_list.clear()
        self.interactable_list.clear()
        self.decor_list.clear()
        self.texts.clear()

        temp_wall = Wall(0, 0)
        grid = int(temp_wall.width) if hasattr(temp_wall, "width") and temp_wall.width > 0 else 64
        half_grid = grid // 2        # 32 px (смещение до центра тайла)

        # Рассчитываем ровное количество столбцов и строк
        columns = config.SCREEN_WIDTH // grid  # 15
        rows = config.SCREEN_HEIGHT // grid    # 10

        center_x = config.SCREEN_WIDTH // 2
        center_y = config.SCREEN_HEIGHT // 2

        for col in range(columns):
            for row in range(rows):
                # Сдвигаем координаты на half_grid
                x = col * grid + half_grid
                y = row * grid + half_grid

                # Создаем пол
                floor = Floor(x, y)

                # Настройка ковра по координатам
                rug_left = center_x - 200 - grid
                rug_right = center_x + 200 + grid

                if rug_left <= x < rug_right and abs(y - center_y) < 150:
                    floor.color = (100, 100, 150)
                else:
                    floor.color = (40, 50, 60)

                self.floor_list.append(floor)

                # Ставим стены строго по внешнему периметру сетки
                if col == 0 or col == columns - 1 or row == 0 or row == rows - 1:
                    self.wall_list.append(Wall(x, y))

        # --- INTERACTABLES ---

        # 1. Wardrobe (Left / Гардероб)
        wardrobe_x = grid * 3 + half_grid
        self.wardrobe = SkinChanger(wardrobe_x, center_y)
        self.interactable_list.append(self.wardrobe)

        for offset_y in [-2, 2]:
            decor = arcade.Sprite(":resources:images/tiles/boxCrate_double.png")
            decor.width = grid
            decor.height = grid
            decor.center_x = wardrobe_x
            decor.center_y = center_y + offset_y * grid
            self.wall_list.append(decor)

        back_wall_x = wardrobe_x - grid
        for i in range(-2, 2):
            decor = arcade.Sprite(":resources:images/tiles/boxCrate_double.png")
            decor.width = grid
            decor.height = grid
            decor.center_x = back_wall_x
            decor.center_y = center_y + i * grid + half_grid
            self.wall_list.append(decor)

        # Подпись над гардеробом
        self.texts.append(
            arcade.Text(
                "WARDROBE",
                wardrobe_x,
                center_y + grid * 2 + 30,
                arcade.color.WHITE,
                font_size=14,
                bold=True,
                anchor_x="center"
            )
        )

        # 2. Armory stand (Right / Оружейная)
        weapon_x = config.SCREEN_WIDTH - (grid * 3 + half_grid)
        self.weapon_stand = WeaponStand(weapon_x, center_y)
        self.interactable_list.append(self.weapon_stand)

        for offset_y in [-2, 2]:
            decor = arcade.Sprite(":resources:images/tiles/boxCrate_double.png")
            decor.width = grid
            decor.height = grid
            decor.center_x = weapon_x
            decor.center_y = center_y + offset_y * grid
            self.wall_list.append(decor)

        back_wall_x_right = weapon_x + grid
        for i in range(-2, 2):
            decor = arcade.Sprite(":resources:images/tiles/boxCrate_double.png")
            decor.width = grid
            decor.height = grid
            decor.center_x = back_wall_x_right
            decor.center_y = center_y + i * grid + half_grid
            self.wall_list.append(decor)

        # Подпись над оружейной
        self.texts.append(
            arcade.Text(
                "ARMORY STAND",
                weapon_x,
                center_y + grid * 2 + 30,
                arcade.color.WHITE,
                font_size=14,
                bold=True,
                anchor_x="center"
            )
        )

        # 3. Portal (Top)
        self.portal = Portal(center_x, 0)
        self.portal.width = grid * 6
        self.portal.height = grid * 3
        self.portal.center_x = center_x
        self.portal.center_y = config.SCREEN_HEIGHT - (grid * 3)

        self.interactable_list.append(self.portal)

    def draw(self):
        """Вызывать в main.py при отрисовке лобби"""
        self.floor_list.draw()
        self.wall_list.draw()
        self.decor_list.draw()
        self.interactable_list.draw()

        # Отрисовка текстовых надписей
        for text in self.texts:
            text.draw()