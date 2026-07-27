import random
import math
import arcade
import config
import database
from entities.player import Player
from entities.items import CrystalDrop, Chest, ShieldItem, WeaponDrop, Portal
from enemies.base_enemy import Zombie, Robot, Slime, Bat
from enemies.boss import Boss  # Импортируем босса
from world.level_generator import LevelGenerator
from world.lobby import Lobby
from ui.hud import HUD
from ui.menus import MenuRenderer
from ui.skin_menu import SkinMenu
from ui.weapon_menu import WeaponMenu
from engine.game_state import GameState
from utils.particle_system import ParticleSystem
from weapons.weapons import MeleeWeapon, RangedWeapon


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.SCREEN_TITLE)
        arcade.set_background_color(config.BG_COLOR)

        self.current_state = GameState.MENU
        self.menu_renderer = MenuRenderer()
        self.hud = None
        self.player_list = None
        self.player = None
        self.level_generator = None
        self.lobby = None
        self.skin_menu = None
        self.weapon_menu = None
        self.physics_engine = None
        self.bullet_list = None
        self.enemy_bullet_list = None
        self.particle_system = ParticleSystem()
        # Звуки
        self.shoot_sound = arcade.load_sound(":resources:sounds/laser1.wav")
        self.enemy_death_sound = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.player_death_sound = arcade.load_sound(":resources:sounds/gameover2.wav")
        self.victory_sound = arcade.load_sound(":resources:sounds/upgrade4.wav")
        self.camera = None

        self.dungeon_level = 1
        self.current_room_key = None

        self.interact_text = arcade.Text(text="", x=config.SCREEN_WIDTH // 2, y=config.SCREEN_HEIGHT // 2 + 50,
                                         color=arcade.color.WHITE, font_size=14, anchor_x="center")
        self.lobby_crystal_text = arcade.Text(text="", x=20, y=config.SCREEN_HEIGHT - 40, color=arcade.color.CYAN,
                                              font_size=20)
        self.press_e_text = arcade.Text("Press [E]", 0, 0, arcade.color.WHITE, 12, anchor_x="center")
        # Текст щита и уровня
        self.shield_text = arcade.Text("", 20, config.SCREEN_HEIGHT - 80, arcade.color.CYAN, 16)
        # Размещаем уровень чуть ниже счета, чтобы надписи не накладывались
        self.level_text = arcade.Text("", config.SCREEN_WIDTH - 100, config.SCREEN_HEIGHT - 70, arcade.color.GOLD, 16)

        self.setup_system()

    def setup_system(self):
        self.player_list = arcade.SpriteList()
        self.camera = arcade.Camera2D()
        self.player = Player(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        self.player_list.append(self.player)
        self.particle_system = ParticleSystem()
        self.hud = HUD()

    def open_skin_menu(self):
        self.current_state = GameState.SKIN_SELECT
        self.skin_menu = SkinMenu(self.player)

    def open_weapon_menu(self):
        # Обновляем кристаллы из БД перед открытием меню
        self.player.update_crystals_from_db()
        self.current_state = GameState.WEAPON_SELECT
        self.weapon_menu = WeaponMenu(self.player)

    def enter_lobby(self):
        self.current_state = GameState.LOBBY
        self.lobby = Lobby()
        self.lobby.setup()
        self.player.center_x = config.SCREEN_WIDTH // 2
        self.player.center_y = 250
        obstacles = arcade.SpriteList()
        obstacles.extend(self.lobby.wall_list)
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, obstacles)
        self.camera.position = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()

    def start_dungeon_run(self):
        self.current_state = GameState.PLAYING
        self.level_generator = LevelGenerator()
        self.dungeon_level = 1
        self.start_new_level()

    def start_new_level(self):
        # Генерируем с учетом уровня (чтобы заспавнить босса на 3-м)
        self.level_generator.generate_level(self.player, self.dungeon_level)
        self.update_physics_engine()
        self.camera.position = (self.player.center_x, self.player.center_y)
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.current_room_key = None
        print(f"--- LEVEL {self.dungeon_level} STARTED ---")

    def update_physics_engine(self):
        obstacles = arcade.SpriteList()
        obstacles.extend(self.level_generator.wall_list)
        obstacles.extend(self.level_generator.door_list)
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, obstacles)

    # --- СИСТЕМА ВОЛН И КОМНАТ ---
    def update_room_logic(self):
        px = self.player.center_x
        py = self.player.center_y
        ts = self.level_generator.tile_size
        pgx, pgy = px / ts, py / ts

        # 1. Поиск комнаты
        found_key = None
        for key, data in self.level_generator.rooms_data.items():
            rect = data['rect']
            if (pgx > rect.left and pgx < rect.right and
                    pgy > rect.bottom and pgy < rect.top):
                found_key = key
                break

        # 2. Вход в новую комнату
        if found_key and found_key != self.current_room_key:
            self.current_room_key = found_key
            self.on_enter_room(found_key)

        # 3. Обновление текущей комнаты (спавн волн)
        if self.current_room_key:
            self.update_active_room(self.current_room_key)

    def on_enter_room(self, room_key):
        room_data = self.level_generator.rooms_data.get(room_key)

        if room_data and not room_data['cleared'] and not room_data['active']:
            print("Entering combat room!")
            room_data['active'] = True

            # Закрываем двери
            for door in room_data['doors']:
                door.center_x = door.initial_x
                door.center_y = door.initial_y
            self.update_physics_engine()

            # Запускаем первую волну
            self.spawn_next_wave(room_data)

    def spawn_next_wave(self, room_data):
        room_data['waves_current'] += 1
        wave_num = room_data['waves_current']
        print(f"Spawning Wave {wave_num}/{room_data['waves_total']}")

        rect = room_data['rect']
        ts = self.level_generator.tile_size

        min_x = (rect.left + 1) * ts
        max_x = (rect.right - 1) * ts
        min_y = (rect.bottom + 1) * ts
        max_y = (rect.top - 1) * ts

        room_rect_px = arcade.LRBT(min_x, max_x, min_y, max_y)

        # Босс
        if room_data['is_boss_room']:
            boss_x = (min_x + max_x) / 2
            boss_y = (min_y + max_y) / 2
            boss = Boss(boss_x, boss_y, self.player, room_rect_px)
            self.level_generator.enemy_list.append(boss)
            return

        # ИЗМЕНЕНИЕ: Спавним всего 1 врага, чтобы быстро пройти
        count = 1

        for _ in range(count):
            ex = random.randint(int(min_x), int(max_x))
            ey = random.randint(int(min_y), int(max_y))

            r = random.random()
            if r < 0.4:
                en = Zombie(ex, ey, self.player, room_rect_px)
            elif r < 0.7:
                en = Robot(ex, ey, self.player, room_rect_px)
            elif r < 0.9:
                en = Bat(ex, ey, self.player, room_rect_px)
            else:
                en = Slime(ex, ey, self.player, room_rect_px)

            self.level_generator.enemy_list.append(en)

    def update_active_room(self, room_key):
        room_data = self.level_generator.rooms_data.get(room_key)
        if not room_data or room_data['cleared']:
            return

        # Считаем врагов
        enemies_alive = 0
        rect = room_data['rect']
        ts = self.level_generator.tile_size

        # Проверяем, есть ли враги ВНУТРИ этой комнаты (используем границы)
        for enemy in self.level_generator.enemy_list:
            if hasattr(enemy, 'room_rect'):
                if (enemy.center_x > (rect.left * ts) and enemy.center_x < (rect.right * ts) and
                        enemy.center_y > (rect.bottom * ts) and enemy.center_y < (rect.top * ts)):
                    enemies_alive += 1

        # Если врагов нет
        if enemies_alive == 0:
            if room_data['waves_current'] < room_data['waves_total']:
                # Спавним следующую волну
                self.spawn_next_wave(room_data)
            else:
                # Все волны пройдены -> КОМНАТА ЗАЧИЩЕНА
                room_data['cleared'] = True
                print("Room Cleared! Doors opening.")
                for door in room_data['doors']:
                    door.center_x = -10000
                self.update_physics_engine()

    # ---------------------------

    def on_mouse_motion(self, x, y, dx, dy):
        if self.current_state == GameState.PLAYING and self.player:
            world_x, world_y, _ = self.camera.unproject((x, y))
            diff_x = world_x - self.player.center_x
            diff_y = world_y - self.player.center_y
            angle_rad = math.atan2(diff_y, diff_x)
            angle_deg = math.degrees(angle_rad)
            self.player.mouse_angle = angle_deg

    def on_draw(self):
        self.clear()
        if self.camera: 
            self.camera.use()

        if self.current_state == GameState.LOBBY:
            if self.lobby:
                self.lobby.draw()
            self.player_list.draw()
            self.player.weapon_list.draw()
            if self.interact_text.text:
                self.interact_text.draw()
        elif self.current_state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
            self.draw_game()

        self.default_camera.use()

        if self.current_state == GameState.PLAYING:
            self.hud.draw(self.player)
            if self.player.armor > 0:
                self.shield_text.text = f"Shield: {int(self.player.armor)}"
                self.shield_text.draw()
            self.level_text.text = f"Level: {self.dungeon_level}"
            self.level_text.draw()
        elif self.current_state == GameState.LOBBY:
            self.lobby_crystal_text.text = f"Crystals: {self.player.crystals}"
            self.lobby_crystal_text.draw()
        elif self.current_state == GameState.MENU:
            self.menu_renderer.draw_main_menu()
        elif self.current_state == GameState.PAUSED:
            self.hud.draw(self.player)
            self.menu_renderer.draw_pause_menu()
        elif self.current_state == GameState.GAME_OVER:
            self.menu_renderer.draw_game_over(self.player.score)
        elif self.current_state == GameState.VICTORY:
            self.menu_renderer.draw_victory(self.player.score)
        elif self.current_state == GameState.SKIN_SELECT:
            self.skin_menu.draw()
        elif self.current_state == GameState.WEAPON_SELECT:
            self.weapon_menu.draw()

    def draw_game(self):
        self.level_generator.floor_list.draw()
        self.level_generator.wall_list.draw()
        self.level_generator.door_list.draw()
        self.level_generator.item_list.draw()
        self.level_generator.portal_list.draw()
        self.level_generator.enemy_list.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.player_list.draw()
        self.player.weapon_list.draw()
        self.particle_system.draw()

        for item in self.level_generator.item_list:
            if isinstance(item, Chest):
                dist = math.dist((self.player.center_x, self.player.center_y), (item.center_x, item.center_y))
                if dist < 100:
                    self.press_e_text.x = item.center_x
                    self.press_e_text.y = item.center_y + 40
                    self.press_e_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.current_state in [GameState.SKIN_SELECT, GameState.WEAPON_SELECT]:
                self.enter_lobby()
            else:
                arcade.close_window()

        if self.current_state == GameState.MENU:
            if key == arcade.key.ENTER:
                self.enter_lobby()

        elif self.current_state == GameState.LOBBY:
            if key == arcade.key.W or key == arcade.key.UP:
                self.player.change_y = config.PLAYER_SPEED
            elif key == arcade.key.S or key == arcade.key.DOWN:
                self.player.change_y = -config.PLAYER_SPEED
            elif key == arcade.key.A or key == arcade.key.LEFT:
                self.player.change_x = -config.PLAYER_SPEED
            elif key == arcade.key.D or key == arcade.key.RIGHT:
                self.player.change_x = config.PLAYER_SPEED

            if key == arcade.key.E:
                hit_list = arcade.check_for_collision_with_list(self.player, self.lobby.interactable_list)
                if hit_list:
                    item = hit_list[0]
                    item.on_interact(self.player, self)

        elif self.current_state == GameState.SKIN_SELECT:
            if self.skin_menu.on_key_press(key) == "EXIT": self.enter_lobby()
        elif self.current_state == GameState.WEAPON_SELECT:
            if self.weapon_menu.on_key_press(key) == "EXIT": self.enter_lobby()

        elif self.current_state == GameState.PLAYING:
            if key == arcade.key.W or key == arcade.key.UP:
                self.player.change_y = config.PLAYER_SPEED
            elif key == arcade.key.S or key == arcade.key.DOWN:
                self.player.change_y = -config.PLAYER_SPEED
            elif key == arcade.key.A or key == arcade.key.LEFT:
                self.player.change_x = -config.PLAYER_SPEED
            elif key == arcade.key.D or key == arcade.key.RIGHT:
                self.player.change_x = config.PLAYER_SPEED
            if key == arcade.key.P: self.current_state = GameState.PAUSED

            if key == arcade.key.E:
                if self.level_generator is not None:
                    closest_chest = None
                    min_dist = 100
                    for item in self.level_generator.item_list:
                        if isinstance(item, Chest):
                            dist = math.dist((self.player.center_x, self.player.center_y),
                                             (item.center_x, item.center_y))
                            if dist < min_dist:
                                min_dist = dist
                                closest_chest = item
                    if closest_chest:
                        drop = closest_chest.open()
                        if drop:
                            self.level_generator.item_list.append(drop)
                        closest_chest.kill()
                        if closest_chest in self.level_generator.wall_list:
                            self.level_generator.wall_list.remove(closest_chest)
                        self.update_physics_engine()

        elif self.current_state in [GameState.GAME_OVER, GameState.VICTORY]:
            if key == arcade.key.R:
                self.player.hp = self.player.max_hp
                self.enter_lobby()

    def on_key_release(self, key, modifiers):
        if self.current_state in [GameState.PLAYING, GameState.LOBBY]:
            if key == arcade.key.W or key == arcade.key.UP:
                if self.player.change_y > 0: self.player.change_y = 0
            elif key == arcade.key.S or key == arcade.key.DOWN:
                if self.player.change_y < 0: self.player.change_y = 0
            elif key == arcade.key.A or key == arcade.key.LEFT:
                if self.player.change_x < 0: self.player.change_x = 0
            elif key == arcade.key.D or key == arcade.key.RIGHT:
                if self.player.change_x > 0: self.player.change_x = 0

    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_state == GameState.PLAYING:
            if button == arcade.MOUSE_BUTTON_LEFT:
                weapon = self.player.weapon
                if isinstance(weapon, RangedWeapon):
                    world_x, world_y, _ = self.camera.unproject((x, y))
                    bullet = weapon.attack(self.player.center_x, self.player.center_y, world_x, world_y)
                    if bullet:
                        self.bullet_list.append(bullet)
                        arcade.play_sound(self.shoot_sound)
                elif isinstance(weapon, MeleeWeapon):
                    hit_enemies = weapon.attack(self.player, self.level_generator.enemy_list)
                    if hit_enemies:
                        self.particle_system.add_hit_effect(self.player.center_x, self.player.center_y,
                                                            arcade.color.YELLOW)
                        for enemy in hit_enemies:
                            self.particle_system.add_hit_effect(enemy.center_x, enemy.center_y, arcade.color.RED)
                            enemy.take_damage(weapon.damage)
                            if enemy.hp <= 0 and not (hasattr(enemy, 'is_dying') and enemy.is_dying):
                                arcade.play_sound(self.enemy_death_sound)
                                if isinstance(enemy, Boss):
                                    self.current_state = GameState.VICTORY
                                    arcade.play_sound(self.victory_sound)
                                crystal = CrystalDrop(enemy.center_x, enemy.center_y, amount=5)
                                self.level_generator.item_list.append(crystal)
                                self.player.score += 10
                                self.particle_system.add_hit_effect(enemy.center_x, enemy.center_y,
                                                                    arcade.color.DARK_RED)

        elif self.current_state == GameState.WEAPON_SELECT:
            self.weapon_menu.on_mouse_press(x, y)
        elif self.current_state == GameState.SKIN_SELECT:
            self.skin_menu.on_mouse_press(x, y)

    def on_update(self, delta_time):
        if self.current_state == GameState.LOBBY:
            self.update_lobby(delta_time)
        elif self.current_state == GameState.PLAYING:
            self.update_game(delta_time)

    def update_lobby(self, delta_time):
        if not self.physics_engine or not self.lobby:
            return

        self.physics_engine.update()
        self.player_list.update(delta_time)
        self.interact_text.text = ""
        closest_item = arcade.check_for_collision_with_list(self.player, self.lobby.interactable_list)
        if closest_item:
            item = closest_item[0]
            self.interact_text.text = item.text
            self.interact_text.x = self.player.center_x
            self.interact_text.y = self.player.center_y + 50

    def update_game(self, delta_time):
        self.physics_engine.update()
        self.player.update(delta_time)
        self.bullet_list.update(delta_time)
        self.enemy_bullet_list.update(delta_time)

        all_obstacles = arcade.SpriteList()
        all_obstacles.extend(self.level_generator.wall_list)
        all_obstacles.extend(self.level_generator.door_list)

        enemies_to_remove = []
        for enemy in self.level_generator.enemy_list:
            if hasattr(enemy, 'is_dying') and enemy.is_dying:
                if enemy.update_death_animation(delta_time):
                    enemies_to_remove.append(enemy)
                continue
            
            result = enemy.update_with_physics(delta_time, all_obstacles)
            if result:
                if isinstance(result, list):
                    self.enemy_bullet_list.extend(result)
                else:
                    self.enemy_bullet_list.append(result)
        
        for enemy in enemies_to_remove:
            if enemy in self.level_generator.enemy_list:
                self.level_generator.enemy_list.remove(enemy)

        self.particle_system.update()
        self.level_generator.item_list.update(delta_time)
        self.level_generator.door_list.update(delta_time)
        self.scroll_to_player()

        self.update_room_logic()

        all_cleared = True
        for key, data in self.level_generator.rooms_data.items():
            if not data['cleared']:
                all_cleared = False
                break

        if all_cleared:
            for p in self.level_generator.portal_list:
                p.alpha = 255
                p.update(delta_time)

            if arcade.check_for_collision_with_list(self.player, self.level_generator.portal_list):
                self.dungeon_level += 1
                self.player.hp = min(self.player.hp + 20, self.player.max_hp)
                self.start_new_level()
                return

        walls_and_doors = [self.level_generator.wall_list, self.level_generator.door_list]
        for bullet in self.bullet_list:
            if arcade.check_for_collision_with_lists(bullet, walls_and_doors):
                self.particle_system.add_hit_effect(bullet.center_x, bullet.center_y, arcade.color.GRAY)
                bullet.kill()
                continue
            hit_enemies = arcade.check_for_collision_with_list(bullet, self.level_generator.enemy_list)
            if len(hit_enemies) > 0:
                bullet.kill()
                for enemy in hit_enemies:
                    self.particle_system.add_hit_effect(enemy.center_x, enemy.center_y, arcade.color.RED)
                    enemy.take_damage(bullet.damage)
                    if enemy.hp <= 0 and not (hasattr(enemy, 'is_dying') and enemy.is_dying):
                        arcade.play_sound(self.enemy_death_sound)
                        if isinstance(enemy, Boss):
                            self.current_state = GameState.VICTORY
                            arcade.play_sound(self.victory_sound)
                        crystal = CrystalDrop(enemy.center_x, enemy.center_y, amount=5)
                        self.level_generator.item_list.append(crystal)
                        self.player.score += 10

        for bullet in self.enemy_bullet_list:
            if arcade.check_for_collision_with_lists(bullet, walls_and_doors):
                bullet.kill()
                continue
            if arcade.check_for_collision(self.player, bullet):
                bullet.kill()
                self.player.take_damage(config.ROBOT_DAMAGE)
                self.particle_system.add_hit_effect(self.player.center_x, self.player.center_y, arcade.color.RED)
                if self.player.hp <= 0:
                    arcade.play_sound(self.player_death_sound)
                    self.current_state = GameState.GAME_OVER

        for enemy in self.level_generator.enemy_list:
            if arcade.check_for_collision(self.player, enemy):
                self.player.take_damage(enemy.damage * 0.05)
                if self.player.hp <= 0:
                    arcade.play_sound(self.player_death_sound)
                    self.current_state = GameState.GAME_OVER

        hit_items = arcade.check_for_collision_with_list(self.player, self.level_generator.item_list)
        for item in hit_items:
            if isinstance(item, Chest):
                continue
            if isinstance(item, WeaponDrop):
                item.on_pickup(self.player)
                item.kill()
            elif isinstance(item, CrystalDrop):
                database.add_crystals(item.amount)
                self.player.update_crystals_from_db()
                item.kill()
            elif item.on_pickup(self.player):
                item.kill()

    def scroll_to_player(self):
        cur_x, cur_y = self.camera.position
        dest_x, dest_y = self.player.center_x, self.player.center_y
        speed = 0.1
        self.camera.position = (cur_x + (dest_x - cur_x) * speed, cur_y + (dest_y - cur_y) * speed)


def main():
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()