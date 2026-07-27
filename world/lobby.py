import arcade
import config
from world.tiles import Wall, Floor
from entities.interactables import Portal, SkinChanger, WeaponStand


class Lobby:
    def __init__(self):
        self.wall_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.interactable_list = arcade.SpriteList()
        self.decor_list = arcade.SpriteList()  # For furniture

    def setup(self):
        temp_wall = Wall(0, 0)
        grid = int(temp_wall.width)  # 64 px
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
                rug_left = center_x - 200 + grid
                rug_right = center_x + 200 

                if rug_left <= x < rug_right and abs(y - center_y) < 150:
                    floor.color = (100, 100, 150)
                else:
                    floor.color = (40, 50, 60)

                self.floor_list.append(floor)

                # Ставим стены строго по внешнему периметру сетки
                if col == 0 or col == columns - 1 or row == 0 or row == rows - 1:
                    self.wall_list.append(Wall(x, y))

        # --- INTERACTABLES ---


        # 1. Wardrobe (Left)
        self.wardrobe = SkinChanger(200, center_y)
        self.interactable_list.append(self.wardrobe)

        # Add "cupboards" around wardrobe for decoration
        for i in range(-1, 2, 2):
            decor = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", 0.5)
            decor.center_x = 200
            decor.center_y = center_y + i * 60
            self.wall_list.append(decor)

        # 2. Armory stand (Right) - открывает меню оружия
        self.weapon_stand = WeaponStand(config.SCREEN_WIDTH - 200, center_y)
        self.interactable_list.append(self.weapon_stand)

        # "Table" under the weapon
        table = arcade.Sprite(":resources:images/tiles/boxCrate_single.png", 0.5)
        table.center_x = config.SCREEN_WIDTH - 200
        table.center_y = center_y
        self.decor_list.append(table)

        # 3. Portal (Top)
        self.portal = Portal(center_x, config.SCREEN_HEIGHT - 100)
        self.interactable_list.append(self.portal)

        # # 4. TV/Sofa (Bottom) - FIXED RESOURCE PATH
        # # Changed bridgeLogs.png to boxCrate_double.png because bridgeLogs was removed in Arcade 3.0
        # sofa = arc
        # self.wall_list.append(sofa)ade.Sprite(":resources:images/tiles/boxCrate_double.png", 0.8)
        # sofa.center_x = center_x
        # sofa.center_y = 150
        # # Color it slightly to look different
        # sofa.color = (150, 100, 100)