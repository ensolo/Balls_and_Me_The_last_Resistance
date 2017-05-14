import pygame
from pygame.locals import *
from sys import exit
from random import *
from math import *


class Vector2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def get_cords(self):
        return self.x, self.y

    def get_magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalize(self):
        magnitude = self.get_magnitude()
        if magnitude != 0:
            self.x /= magnitude
            self.y /= magnitude


class Game(object):
    def __init__(self):
        self.score = 0
        self.highscore = 0
        self.bullets = []
        self.enemies = []
        self.items = []
        self.boss_spawn = 50

    def spawn_enemy(self):
        for _ in range(randint(1, 1 + int((difficulty * time.time_total_seconds) ** 0.5))):
            x, y = self.get_spawn_cords(save_zone)
            self.enemies.append(Enemy(x, y, randint(10, 60),
                                        randint(100, 200 + int((difficulty * time.time_total_seconds) ** 0.5) * 50),
                                        randint(1, 1 + int((difficulty * time.time_total_seconds) ** 0.5))))

    def get_spawn_cords(self, save_zone):
        lx = []
        ly = []
        l_result = []
        if 71 < player.x - save_zone:
            lx.append([randint(71, player.x - save_zone), player.x - save_zone - 71])
        if player.x + save_zone < w - 71:
            lx.append([randint(player.x + save_zone, w - 71), w - 71 - player.x - save_zone])
        if 71 < player.y - save_zone:
            ly.append([randint(71, player.y - save_zone), player.y - save_zone - 71])
        if player.y + save_zone < h - 71:
            ly.append([randint(player.y + save_zone, h - 71), h - 71 - player.y - save_zone])
        total = 0
        for x in lx:
            for y in ly:
                total += x[1] * y[1]
                l_result.append([total, x[0], y[0]])
        num = randint(0, total)
        for result in l_result:
            if num <= result[0]:
                x, y = result[1:]
                return x, y

    def spawn_item(self, type):
        if type == "immortal":
            self.items.append(Immortal((128, 0, 128), 5))
        if type == "rapid_fire":
            self.items.append(RapidFire((128, 0, 128), 5))

    def give_highscore(self):
        score_file = open("Highscore.txt", "a+")
        score_file.close()
        score_file = open("Highscore.txt", "r+")
        highscore = score_file.read()
        if len(highscore) == 0:
            self.highscore = 0
        else:
            self.highscore = int(highscore)
        if self.highscore < self.score:
            score_file.seek(0, 0)
            score_file.write(repr(self.score))
            self.highscore = self.score
        score_file.close()

    def create_objects(self):
        if self.score >= self.boss_spawn and not boss1.active:
            if time.timer_boss1_delay > 5000:
                time.timer_boss1_delay = 0
                self.bullets = []
            boss1.spawn(int(self.boss_spawn / 5), int(self.boss_spawn / 5))
        if boss1.active:
            boss1.fire()
            for part in boss1.parts:
                part.fire()
        if pygame.mouse.get_pressed()[0] and time.timer_firerate > player.firerate:
            time.timer_firerate = 0
            player.fire()
        if time.timer_enemy > 1400 and not boss1.active and time.timer_boss1_delay > 5000:
            time.timer_enemy = 0
            self.spawn_enemy()
        if time.timer_item > 20000 and not boss1.active and time.timer_boss1_delay > 5000:
            time.timer_item = 0
            number = randint(1, 2)
            if number == 1:
                self.spawn_item("immortal")
            elif number == 2:
                self.spawn_item("rapid_fire")

    def delete_objects(self):
        for bullet in self.bullets:
            for enemy in self.enemies:
                bullet.collision(enemy, "enemy")
            if boss1.active:
                for part in boss1.parts:
                    bullet.collision(part, "part")
                bullet.collision(boss1, "boss1")

    def draw_all(self, type):
        if type == "start":
            screen.blit(background_start, (0, 0))
            start_font.draw()
            cursor.draw()
        if type == "game":
            screen.blit(background_game, (0, 0))
            if boss1.active:
                boss1.draw()
            if boss1.active:
                for enemy_bullets in boss1.enemy_bullets:
                    enemy_bullets.draw()
            for bullet in self.bullets:
                bullet.draw()
            player.draw()
            for enemy in self.enemies:
                enemy.draw()
            for item in self.items:
                item.draw()
            score_font.draw("Score " + str(self.score))
            cursor.draw()
        if type == "over":
            screen.blit(background_game, (0, 0))
            if boss1.active:
                boss1.draw()
                for enemy_bullet in boss1.enemy_bullets:
                    enemy_bullet.draw()
            for bullet in self.bullets:
                bullet.draw()
            player.draw()
            for enemy2 in self.enemies:
                enemy2.draw()
            for item in self.items:
                item.draw()
            game_over_font.draw()
            restart_font.draw()
            highscore_font.draw("Highscore  " + repr(self.highscore))
            cursor.draw()

    def update_all(self):
        time.update_time()
        player.update_cords()
        if boss1.active:
            boss1.update()
            for enemy_bullet in boss1.enemy_bullets:
                enemy_bullet.update()
        for bullet in self.bullets:
            bullet.update_cords()
        for enemy in self.enemies:
            enemy.update_cords()
        for item in self.items:
            item.update()

    def restart(self):
        self.bullets = []
        self.enemies = []
        self.items = []
        self.clear_effects()
        self.boss_spawn = 50
        boss1.parts = []
        boss1.enemy_bullets = []
        boss1.delete()
        player.x = int(w / 2)
        player.y = int(h / 2)
        self.score = 0
        time.timer_boss1_delay = 0
        time.time_total_seconds = 0
        time.restart()

    def clear_effects(self):
        player.speed = me_speed
        player.firerate = firerate
        player.can_fire = True
        player.invisible = False

    def over_loop(self):
        pressed_keys = pygame.key.get_pressed()
        while not pressed_keys[K_SPACE]:
            menu.menu_loop()
            pressed_keys = pygame.key.get_pressed()
            self.draw_all("over")
            pygame.display.update()

    def start_loop(self):
        pressed_keys = pygame.key.get_pressed()
        while not pressed_keys[K_SPACE]:
            menu.menu_loop()
            pressed_keys = pygame.key.get_pressed()
            self.draw_all("start")
            pygame.display.update()

    def check_over(self):
        for enemy in self.enemies:
            if enemy.check_collision():
                self.over_init()
        for enemy_bullet in boss1.enemy_bullets:
            if enemy_bullet.check_collision():
                self.over_init()

    def over_init(self):
        self.give_highscore()
        self.over_loop()
        self.restart()


class Player(object):
    def __init__(self, x, y, radius, spirit, speed, firerate):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.direction_x = None
        self.direction_y = None
        self.spirit = spirit
        self.can_fire = True
        self.invisible = False
        self.firerate = firerate
        self.boost = 1000
        self.boost_active = False

    def __sub__(self, other):
        return self.x - other.x, self.y - other.y

    def get_pos(self):
        return self.x, self.y

    def draw(self):
        x_spirit = self.x - self.spirit.get_width() / 2
        y_spirit = self.y - self.spirit.get_height() / 2
        screen.blit(self.spirit, (x_spirit, y_spirit))

    def get_direction(self):
        pressed_keys = pygame.key.get_pressed()
        key_direction = Vector2(0, 0)
        if pressed_keys[K_w] and player.y > player.radius:
            key_direction.y = -1
        if pressed_keys[K_s] and player.y < h - player.radius:
            key_direction.y = 1
        if pressed_keys[K_a] and player.x > player.radius:
            key_direction.x = -1
        if pressed_keys[K_d] and player.x < w - player.radius:
            key_direction.x = 1
        if not self.boost_active and pressed_keys[K_SPACE] and time.timer_boost > 5000:
            time.countdown_boost = 0
            game.items.append(Boost((153, 51, 155), -5))
            self.boost_active = True
        if self.boost_active and time.countdown_boost > 200:
            time.timer_boost = 0
            self.boost_active = False
        if not self.can_fire:
            angle = degrees(atan2(key_direction.x, key_direction.y))
            self.spirit = pygame.transform.rotate(orig_me_spirit, angle + 230)
        key_direction.normalize()
        self.direction_x, self.direction_y = key_direction.get_cords()

    def fire(self):
        if self.can_fire:
            sound_fire.stop()
            sound_fire.play()
            mouse_cords = pygame.mouse.get_pos()
            mouse_direction.x = mouse_cords[0] - self.x
            mouse_direction.y = mouse_cords[1] - self.y
            mouse_direction.normalize()
            game.bullets.append(Bullet((mouse_direction.get_cords())))
            angle = degrees(atan2(mouse_cords[0] - self.x, mouse_cords[1] - self.y))
            self.spirit = pygame.transform.rotate(orig_me_spirit, angle + 230)

    def update_cords(self):
        if self.boost_active:
            self.x += int(self.direction_x * (self.speed + self.boost) * time.time_passed_seconds)
            self.y += int(self.direction_y * (self.speed + self.boost) * time.time_passed_seconds)
        else:
            self.x += int(self.direction_x * self.speed * time.time_passed_seconds)
            self.y += int(self.direction_y * self.speed * time.time_passed_seconds)


class Enemy(object):
    def __init__(self, x, y, radius, speed, lives):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.direction = None
        self.lives = lives

    def get_pos(self):
        return self.x, self.y

    def draw(self):
        pygame.draw.circle(screen, COLOR_L[self.lives], (self.x, self.y), self.radius)

    def update_cords(self):
        direction = Vector2(player.x - self.x, player.y - self.y)
        self.direction = (direction.get_cords())
        direction.normalize()
        self.x += int(direction.x * self.speed * time.time_passed_seconds)
        self.y += int(direction.y * self.speed * time.time_passed_seconds)

    def check_collision(self):
        try:
            direction = Vector2(self.direction[0], self.direction[1])
            distance = direction.get_magnitude()
            if distance <= self.radius + player.radius:
                if not player.invisible:
                    return True
                game.score += 1
                self.delete()
            return False
        except:
            return False

    def delete(self):
        game.enemies.remove(self)


class Bullet(object):
    def __init__(self, vector):
        self.x = player.x
        self.y = player.y
        self.radius = 10
        self.speed = 800
        self.in_air = False
        self.vector = vector

    def draw(self):
        if self.x <= 0 or self.x >= w or self.y <= 0 or self.y >= h:
            self.delete()
        else:
            pygame.draw.circle(screen, (0, 255, 255), (self.x, self.y), self.radius)

    def collision(self, enemy, type):
        if type == "enemy":
            vector = Vector2(self.x - enemy.x, self.y - enemy.y)
            if vector.get_magnitude() <= self.radius + enemy.radius:
                enemy.lives -= 1
                if enemy.lives == 0:
                    enemy.delete()
                    game.score += 1
                self.delete()
        if type == "part":
            vector = Vector2(self.x - enemy.x, self.y - enemy.y)
            if vector.get_magnitude() <= self.radius + enemy.radius:
                enemy.delete()
                self.delete()
        if type == "boss1":
            vector = Vector2(self.x - enemy.x, self.y - enemy.y)
            if vector.get_magnitude() <= self.radius + enemy.radius:
                self.delete()
                if len(boss1.parts) == 0:
                    boss1.lives -= 1
                    if boss1.lives == 0:
                        boss1.delete()

    def update_cords(self):
        self.x += int(self.vector[0] * self.speed * time.time_passed_seconds)
        self.y += int(self.vector[1] * self.speed * time.time_passed_seconds)

    def delete(self):
        try:
            game.bullets.remove(self)
        except:
            pass


class Cursor(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.radius = 40

    def draw(self):
        self.update_cords()
        screen.blit(cursor_spirit, (self.x - self.radius / 2, self.y - self.radius / 2))

    def update_cords(self):
        self.x = pygame.mouse.get_pos()[0]
        self.y = pygame.mouse.get_pos()[1]


class Button(object):
    def __init__(self, text, x, y, width, height, font):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = Font(x, y, 3, None, width, height)

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height:
            return True
        return False

    def draw(self):
        if self.hover():
            pygame.draw.rect(screen, (51, 51, 255), (self.x, self.y, self.width, self.height))
            self.font.draw(self.text, (255, 0, 0))
        else:
            pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y, self.width, self.height))
            self.font.draw(self.text, (255, 255, 255))

    def check_pressed(self):
        if self.hover():
            if pygame.mouse.get_pressed()[0]:
                return True
        return False


class Font(object):
    def __init__(self, offset_x, offset_y, font, color, center_w=1920, center_h=1080, center=True, x=0, y=0):
        self.font_big = pygame.font.Font("TannenbergFett.ttf", 100)
        self.font_medium = pygame.font.Font("TannenbergFett.ttf", 50)
        self.font_small = pygame.font.Font("TannenbergFett.ttf", 30)
        self.surface = None
        self.font = font
        self.color = color
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.center = center
        self.x = x
        self.y = y
        self.center_w = center_w
        self.center_h = center_h

    def make_surface(self, text, statement=True):
        if self.font == 1:
            self.surface = self.font_big.render(text, statement, self.color)
        elif self.font == 2:
            self.surface = self.font_medium.render(text, statement, self.color)
        elif self.font == 3:
            self.surface = self.font_small.render(text, statement, self.color)
        self.make_cords()

    def make_cords(self):
        if self.center:
            self.x = (self.center_w - self.surface.get_width()) / 2 + self.offset_x
            self.y = (self.center_h - self.surface.get_height()) / 2 + self.offset_y

    def draw(self, text="none", color=(1, 1, 1)):
        if color != (1, 1, 1):
            self.color = color
        if text != "none":
            self.make_surface(text)
        screen.blit(self.surface, (self.x, self.y))


class Menu(object):
    def __init__(self):
        pass

    def menu_loop(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    while True:
                        esc_pressed = False
                        for event2 in pygame.event.get():
                            if event2.type == KEYDOWN:
                                if event2.key == K_ESCAPE:
                                    esc_pressed = True
                                    break
                        if button_exit.check_pressed():
                            exit()
                        if button_return.check_pressed() or esc_pressed:
                            break
                        screen.blit(background, (0, 0))
                        button_exit.draw()
                        button_return.draw()
                        cursor.draw()
                        pygame.display.update()
                        time.time_passed = clock.tick(60)


class Time(object):
    def __init__(self):
        self.time_passed = None
        self.time_passed_seconds = None
        self.timer_enemy = 0
        self.timer_firerate = 0
        self.timer_item = 0
        self.timer_boss1_fire = 0
        self.timer_boss1_movement = 0
        self.countdown_boost = 0
        self.timer_boost = 0
        self.timer_boss1_delay = 0
        self.time_total_seconds = 0

    def update_time(self):
        self.time_passed = clock.tick(60)
        self.timer_boss1_movement += self.time_passed
        self.timer_boss1_fire += self.time_passed
        self.timer_firerate += self.time_passed
        self.timer_enemy += self.time_passed
        self.timer_item += self.time_passed
        self.countdown_boost += self.time_passed
        self.timer_boost += self.time_passed
        self.timer_boss1_delay += self.time_passed
        self.time_passed_seconds = self.time_passed / 1000.0
        if not boss1.active:
            self.time_total_seconds += self.time_passed_seconds

    def restart(self):
        self.timer_enemy = 0
        self.timer_firerate = 0
        self.timer_item = 0
        self.timer_boss1_movement = 0
        self.timer_boss1_fire = 0
        self.time_total_seconds = 0
        self.countdown_boost = 10000


class Item(object):
    def __init__(self, spirit, duration, letter):
        self.x = randint(50, w - 50)
        self.y = randint(50, h - 50)
        self.radius = 40
        self.spirit = spirit
        self.use = False
        self.despawn = 10
        self.font = Font(self.x, self.y, 3, (255, 255, 255), 0, 0)
        self.duration = duration
        self.letter = letter

    def draw(self):
        self.font.make_surface(self.letter)
        if self.use:
            index = self.items_use_index(self)
            x = w - self.radius - index * (self.radius + 10) * 2
            y = self.radius
            pygame.draw.circle(screen, self.spirit, (x, y), self.radius)
            countdown_font = Font(x, y, 3, (255, 255, 255), 0, 0)
            countdown_font.make_surface(self.duration_display(1))
            countdown_font.draw()
        else:
            pygame.draw.circle(screen, self.spirit, (self.x, self.y), self.radius)
            self.font.draw()

    def check_pickup(self):
        direction = Vector2(self.x - player.x, self.y - player.y)
        if direction.get_magnitude() <= self.radius + player.radius:
            return True
        return False

    def duration_display(self, places):
        duration = modf(self.duration)
        if self.duration >= 0:
            dez_piece = str(list(str(duration[0]))[2:places + 2][0])
            int_piece = str(int(duration[1]))
            return int_piece + "." + dez_piece
        else:
            dez_piece = str(list(str(duration[0]))[3:places + 3][0])
            int_piece = str(int(duration[1]))
            return int_piece + "." + dez_piece

    def items_use_index(self, item):
        result = []
        for element in game.items:
            if element.use:
                result.append(element)
        return result.index(item)

    def delete(self):
        try:
            game.items.remove(self)
        except:
            pass


class Boost(Item):
    def __init__(self, spirit, duration):
        Item.__init__(self, spirit, duration, letter="B")
        self.use = True

    def update(self):
        if self.duration >= 0:
            self.delete()
        if self.duration < 0:
            self.duration += time.time_passed_seconds


class Immortal(Item):
    def __init__(self, spirit, duration):
        Item.__init__(self, spirit, duration, letter="I")
        self.speed = 1000

    def update(self):
        if self.use and self.duration <= 0:
            player.speed = me_speed
            player.can_fire = True
            player.invisible = False
            self.delete()
        if self.use and self.duration > 0:
            self.duration -= time.time_passed_seconds
            player.speed = self.speed
            player.can_fire = False
            player.invisible = True
        if not self.use and self.check_pickup():
            self.use = True
        if self.despawn <= 0 and not self.use:
            self.delete()
        else:
            self.despawn -= time.time_passed_seconds


class RapidFire(Item):
    def __init__(self, spirit, duration):
        Item.__init__(self, spirit, duration, letter="R")
        self.rapid_fire = 50

    def update(self):
        if self.use and self.duration <= 0:
            player.firerate = firerate
            self.delete()
        if self.use and self.duration > 0:
            self.duration -= time.time_passed_seconds
            player.firerate = self.rapid_fire
        if not self.use and self.check_pickup():
            self.use = True
        if self.despawn <= 0 and not self.use:
            self.delete()
        else:
            self.despawn -= time.time_passed_seconds


class Boss1(object):
    def __init__(self, spirit):
        self.x = None
        self.y = None
        self.radius = 70
        self.speed = 200
        self.lives = None
        self.total_lives = None
        self.spirit = spirit
        self.active = False
        self.parts = []
        self.enemy_bullets = []
        self.vector = Vector2(uniform(-1, 1), uniform(-1, 1))

    def spawn(self, num_parts, lives):
        self.vector.normalize()
        self.lives = lives
        self.total_lives = lives
        time.timer_boss1_fire = 0
        game.items = []
        game.enemies = []
        game.clear_effects()
        if time.timer_boss1_delay > 3000:
            self.x, self.y = game.get_spawn_cords(300)
            game.boss_spawn += 75
            self.active = True
            for _ in range(num_parts):
                self.parts.append(Boss1Parts())

    def draw(self):
        pygame.draw.rect(screen, (0, 0, 0), (w / 4, h / 4, w / 2, 10))
        pygame.draw.rect(screen, (255, 0, 0), (w / 4, h / 4, w / 2 * self.lives / self.total_lives, 10))
        pygame.draw.circle(screen, self.spirit, (self.x, self.y), self.radius)
        for part in self.parts:
            part.draw()

    def fire(self):
        if time.timer_boss1_fire > 1500 * int(((len(boss1.parts) + 1) ** 0.5)):
            time.timer_boss1_fire = 0
            for z in range(0, 360, 36):
                vector_x = cos(radians(z))
                vector_y = sin(radians(z))
                vector = Vector2(vector_x, vector_y)
                vector.normalize()
                boss1.enemy_bullets.append(EnemyBullet(self.x, self.y, (0, 0, 255), vector))

    def update(self):
        if time.timer_boss1_movement > 2500:
            time.timer_boss1_movement = 0
            self.vector = Vector2(uniform(-1, 1), uniform(-1, 1))
            self.vector.normalize()
            self.parts.append(Boss1Parts())
        if w - self.radius <= self.x or self.x <= self.radius:
            self.vector.x *= -1
        if h - self.radius <= self.y or self.y <= self.radius:
            self.vector.y *= -1
        self.x += int(self.vector.x * self.speed * time.time_passed_seconds)
        self.y += int(self.vector.y * self.speed * time.time_passed_seconds)
        for part in self.parts:
            part.update()

    def delete(self):
        game.score += 25
        time.timer_boss1_delay = 0
        self.active = False


class Boss1Parts(object):
    def __init__(self):
        self.x = boss1.x
        self.y = boss1.y
        self.radius = 30
        self.speed = 300
        self.spirit = (204, 204, 0)
        self.vector = None

    def draw(self):
        pygame.draw.circle(screen, self.spirit, (self.x, self.y), self.radius)

    def check_collision(self, other):
        direction = Vector2(other.x - self.x, other.y - self.y)
        if direction.get_magnitude() <= self.radius + other.radius:
            return True
        return False

    def fire(self):
        if random() < 0.003:
            vector = Vector2(player.x - self.x, player.y - self.y)
            vector.normalize()
            boss1.enemy_bullets.append(EnemyBullet(self.x, self.y, (0, 0, 255), vector))

    def update(self):
        if self.check_collision(boss1):
            self.vector = Vector2(self.x - boss1.x, self.y - boss1.y)
            self.vector *= 200
        else:
            self.vector = Vector2(boss1.x - self.x, boss1.y - self.y)
            self.vector *= 1
        for part in boss1.parts:
            if self.check_collision(part) and part != self:
                if randint(0, 1):
                    operator_x = 1
                else:
                    operator_x = -1
                if randint(0, 1):
                    operator_y = 1
                else:
                    operator_y = -1
                part_vector_x = part.x - self.x + 2 * self.radius * operator_x
                part_vector_y = part.y - self.y + 2 * self.radius * operator_y
                part_vector = Vector2(part_vector_x, part_vector_y)
                self.vector -= part_vector * 2
        self.vector.normalize()
        self.x += int(self.vector.x * self.speed * time.time_passed_seconds)
        self.y += int(self.vector.y * self.speed * time.time_passed_seconds)

    def delete(self):
        try:
            boss1.parts.remove(self)
        except:
            pass


class EnemyBullet(object):
    def __init__(self, x, y, spirit, vector):
        self.x = x
        self.y = y
        self.radius = 10
        self.spirit = spirit
        self.vector = vector
        self.speed = 800

    def draw(self):
        if self.x <= 0 or self.x >= w or self.y <= 0 or self.y >= h:
            self.delete()
        else:
            pygame.draw.circle(screen, self.spirit, (self.x, self.y), self.radius)

    def check_collision(self):
        try:
            direction = Vector2(self.x - player.x, self.y - player.y)
            distance = direction.get_magnitude()
            if distance <= self.radius + player.radius:
                if not player.invisible:
                    return True
                self.delete()
            return False
        except:
            return False

    def update(self):
        self.x += int(self.vector.x * self.speed * time.time_passed_seconds)
        self.y += int(self.vector.y * self.speed * time.time_passed_seconds)

    def delete(self):
        try:
            boss1.enemy_bullets.remove(self)
        except:
            pass


pygame.init()

w, h = 1920, 1080
firerate = 270
difficulty = 0.1
w_button = 200
h_button = 100
me_radius = 35
save_zone = 200
me_speed = 350
COLOR_L = {1: (255, 0, 0), 2: (255, 128, 0), 3: (255, 255, 0), 4: (128, 255, 0), 5: (0, 255, 0), 6: (0, 255, 128)}

screen = pygame.display.set_mode((w, h), FULLSCREEN, 32)
clock = pygame.time.Clock()

me_spirit_filename = "Me.png"
background_filename = "Background.jpg"
background_start_filename = "Background_start.png"
background_game_filename = "Background_game.png"
cursor_filename = "Cursor.png"
me_spirit_load = pygame.image.load(me_spirit_filename).convert_alpha()
background = pygame.image.load(background_filename).convert()
background_start = pygame.image.load(background_start_filename).convert()
background_game = pygame.image.load(background_game_filename).convert()
cursor_spirit = pygame.image.load(cursor_filename).convert_alpha()
orig_me_spirit = pygame.transform.scale(me_spirit_load, (me_radius * 2, me_radius * 2))
background = pygame.transform.scale(background, (w, h))
background_start = pygame.transform.scale(background_start, (w, h))
background_game = pygame.transform.scale(background_game, (w, h))
cursor_spirit = pygame.transform.scale(cursor_spirit, (40, 40))

music_background_filename = "music_background.mp3"
fire_sound_filename = "fire_sound.ogg"
pygame.mixer.music.load(music_background_filename)
pygame.mixer.music.set_volume(0.5)
sound_fire = pygame.mixer.Sound(fire_sound_filename)
sound_fire.set_volume(0.5)

game = Game()
player = Player(int(w / 2), int(h / 2), me_radius, orig_me_spirit, me_speed, firerate)
boss1 = Boss1((255, 255, 0))
time = Time()
cursor = Cursor()
mouse_direction = Vector2(0, 0)
button_exit = Button("Exit", (w - w_button) / 2, h / 2 + 2 * h_button, w_button, h_button, 3)
button_return = Button("Back to Game", (w - w_button) / 2, h / 2 - 2 * h_button, w_button, h_button, 3)
start_font = Font(0, 0, 2, (255, 255, 255))
start_font.make_surface("Press Space to Start the Game")
score_font = Font(0, 0, 3, (255, 255, 255), w, h, False)
game_over_font = Font(0, 0, 1, (255, 255, 255))
game_over_font.make_surface("Game Over")
restart_font = Font(0, game_over_font.surface.get_height(), 2, (255, 255, 255))
restart_font.make_surface("Press Space to restart the Game")
highscore_font = Font(0, -game_over_font.surface.get_height(), 2, (255, 255, 255))
menu = Menu()

pygame.mouse.set_visible(False)

pygame.mixer.music.play(-1)
game.start_loop()
while True:
    menu.menu_loop()
    player.get_direction()
    game.create_objects()
    game.delete_objects()
    game.draw_all("game")
    game.update_all()
    game.check_over()
    pygame.display.update()
