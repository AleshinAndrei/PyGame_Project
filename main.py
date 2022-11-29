import pygame
import os
import sys
from random import random, sample, choice, randrange
from math import e


GENERATE_PARTICLE = randrange(25, 32)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


def terminate():
    pygame.quit()
    sys.exit()


class MainGame:
    def __init__(self):
        self.lvl_width = None
        self.lvl_height = None
        self.lvl_map = [['@']]
        self.difficulty = 10
        self.closed_road = (0, 0)

        self.load_random_lvl()
        self.WIDTH = 500
        self.HEIGHT = 500
        self.SIZE = (self.WIDTH, self.HEIGHT)
        self.font = pygame.font.Font(None, 30)

        self.clock = pygame.time.Clock()
        self.FPS = 50
        self.dino_FPS = 30
        self.wait_time = 1500

        self.running = True
        self.main_screen = pygame.display.set_mode(self.SIZE)
        self.main_screen.fill((0, 0, 0))

        self.tile_images = {'wall': load_image('wall.png'), 'empty': load_image('ground.png')}
        cup_image = load_image('ground.png')
        cup_image.blit(load_image("cup.png"), (5, 5))
        self.tile_images['cup'] = cup_image

        self.player_image = load_image('mario.png')

        self.tile_width = 50
        self.tile_height = 50

        self.player = None
        self.p_x = 0
        self.p_y = 0

        self.all_sprites = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.particles_group = pygame.sprite.Group()

        self.new_dino_game()
        self.dino_is_active = False
        self.win_dino_game = True

        # сгенерируем частицы разного размера
        self.fire = [load_image("star.png", -1)]
        for scale in (5, 10, 20):
            self.fire.append(pygame.transform.scale(self.fire[0], (scale, scale)))

    def load_random_lvl(self):
        self.lvl_width = 59
        self.lvl_height = 54
        self.lvl_map = []
        self.lvl_map += [['.'] * self.lvl_width for _ in range(5)]
        self.lvl_map += [['#'] * self.lvl_width]
        self.lvl_map[5][self.lvl_width // 4 * 2 + 1] = '.'
        self.lvl_map[2][self.lvl_width // 4 * 2 + 1] = '@'
        for row in range((self.lvl_height - 6) // 2):
            row = ['#'] * self.lvl_width
            for col in range(1, self.lvl_width, 2):
                row[col] = 'C'
            self.lvl_map += [row]
            self.lvl_map += [['#'] * self.lvl_width]

        y = 6
        x = self.lvl_width // 4 * 2 + 1
        self.lvl_map[y][x] = '.'

        count = (self.lvl_height - 6) // 2 * (self.lvl_width // 2) - 1
        queue = [(y, x, 0, 0, None, None)]
        stack = [[queue[0]]]
        while count > 0:
            new_step = []
            new_queue = []
            for y, x, self_lvl, self_index, pre_point_lvl, pre_point_index in queue:
                new_branch = False
                for i, j in sample([(y - 2, x), (y, x + 2), (y + 2, x), (y, x - 2)], k=4):
                    try:
                        cell = self.lvl_map[i][j]
                    except IndexError:
                        continue
                    if cell == 'C':
                        count -= 1
                        self.lvl_map[i][j] = "."
                        self.lvl_map[(y + i) // 2][(x + j) // 2] = "."
                        new_point = (i, j, len(stack), len(new_step), self_lvl, self_index)
                        new_step.append(new_point)
                        new_queue.append(new_point)
                        if random() > 2 / (1 + e ** (-self.difficulty * 0.3)) - 1 or new_branch:
                            break
                        elif not new_branch:
                            new_branch = True
                else:
                    if not new_branch:
                        try:
                            new_queue.append(stack[pre_point_lvl][pre_point_index])
                        except TypeError:
                            pass
            if new_step:
                stack.append(new_step)
            queue = sample(new_queue, len(new_queue))

        i = 0
        while i < self.lvl_width * self.lvl_height * self.difficulty / 1000:
            y = randrange(6, self.lvl_height, 2)
            x = randrange(1, self.lvl_width, 2)
            if self.lvl_map[y][x] == ".":
                self.lvl_map[y][x] = "%"
                i += 1

        while True:
            y = randrange(6, self.lvl_height, 2)
            x = randrange(1, self.lvl_width, 2)
            if self.lvl_map[y][x] == '.':
                self.lvl_map[y][x] = "$"
                break
        self.lvl_map[0][0] = "$"

    def start(self):
        background = pygame.transform.scale(load_image('fon.jpg'), self.SIZE)
        self.main_screen.blit(background, (0, 0))

        intro_text = ['New Game', "Find the Cup", "Press 'space' to start"]
        text_coord = 115
        for line in intro_text:
            string_rendered = self.font.render(line, 1, pygame.Color('darkorange'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.main_screen.blit(string_rendered, intro_rect)

        string_rendered = self.font.render('Created by Aleshin Andrei and Grishina Lena', 1, pygame.Color('darkorange'))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = 10
        intro_rect.top = 475
        self.main_screen.blit(string_rendered, intro_rect)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.main_gameplay()
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def move_player(self, dx, dy):
        if (
                0 <= self.p_x + dx < self.lvl_width and 0 <= self.p_y + dy < self.lvl_height
                and self.lvl_map[self.p_y + dy][self.p_x + dx] in {'.', '%', '$'}
        ):
            if self.lvl_map[self.p_y + dy][self.p_x + dx] == "%":
                self.new_dino_game()
                self.closed_road = (self.p_y + dy, self.p_x + dx)
            else:
                if self.lvl_map[self.p_y + dy][self.p_x + dx] == "$":
                    self.running = False
                self.lvl_map[self.p_y][self.p_x] = '.'
                self.lvl_map[self.p_y + dy][self.p_x + dx] = '@'
                self.p_x += dx
                self.p_y += dy
                self.player.rect = (
                    self.player.rect[0] + dx * self.tile_width, self.player.rect[1] + dy * self.tile_height,
                    self.player.rect[2], self.player.rect[3]
                )

    def new_dino_game(self):
        self.dino_rect = pygame.Rect(0, 0, 500, 500)
        self.dino_is_active = True
        self.win_dino_game = False
        self.dino_game = GoogleDino(self)

    def main_gameplay(self):
        self.generate_level()
        camera = Camera(self)
        while self.running:
            if self.dino_is_active:
                self.main_screen.blit(self.dino_game.update(), self.dino_rect)
                self.dino_is_active, self.win_dino_game = self.dino_game.status()
                if not self.dino_is_active:
                    pygame.display.flip()
                    pygame.time.wait(self.wait_time)
                    if self.win_dino_game:
                        self.lvl_map[self.closed_road[0]][self.closed_road[1]] = '.'
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                        terminate()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.move_player(0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.move_player(0, 1)
                        elif event.key == pygame.K_RIGHT:
                            self.move_player(1, 0)
                        elif event.key == pygame.K_LEFT:
                            self.move_player(-1, 0)
                        elif event.key == pygame.K_p:
                            self.new_dino_game()
                # изменяем ракурс камеры
                camera.update()
                # обновляем положение всех спрайтов
                for sprite in self.all_sprites:
                    camera.apply(sprite)
                self.main_screen.fill((0, 0, 0))
                self.tiles_group.draw(self.main_screen)
                self.player_group.draw(self.main_screen)

                string_rendered = self.font.render("Find the CUP", 2, pygame.Color('darkorange'))
                intro_rect = string_rendered.get_rect()
                intro_rect.top = 10
                intro_rect.x = 180
                self.main_screen.blit(string_rendered, intro_rect)
            pygame.display.flip()
            if self.dino_is_active:
                self.clock.tick(self.dino_FPS)
            else:
                self.clock.tick(self.FPS)
        self.game_end()

    def generate_level(self):
        self.lvl_width = len(self.lvl_map[0])
        self.lvl_height = len(self.lvl_map)
        for y in range(self.lvl_height):
            for x, cell in enumerate(self.lvl_map[y]):
                if cell in {'.', '%'}:
                    Tile('empty', x, y, self)
                elif cell == '#':
                    Tile('wall', x, y, self)
                elif cell == '@':
                    Tile('empty', x, y, self)
                    self.player = Player(x, y, self)
                    self.p_x = x
                    self.p_y = y
                elif cell == "$":
                    Tile('cup', x, y, self)

        self.all_sprites.draw(self.main_screen)

    def game_end(self):
        count = 6

        particle_count = choice([_ for _ in range(20, 40)])
        numbers = range(-5, 6)

        text = 'You Win!!'
        string_rendered = self.font.render(text, 1, pygame.Color('yellow'))
        text_rect = string_rendered.get_rect()
        text_rect.x = 200
        text_rect.top = 200

        pygame.time.set_timer(GENERATE_PARTICLE, 600)
        while count > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                    terminate()
                if event.type == GENERATE_PARTICLE:
                    count -= 1
                    for _ in range(particle_count):
                        Particle(self, self.player.rect[:2], choice(numbers), choice(numbers))

            self.main_screen.fill((0, 0, 0))

            self.tiles_group.draw(self.main_screen)
            self.player_group.draw(self.main_screen)
            self.particles_group.draw(self.main_screen)
            self.particles_group.update()

            self.main_screen.blit(string_rendered, text_rect)
            pygame.display.flip()
            self.clock.tick(self.FPS)

        global main_game
        main_game = MainGame()
        main_game.start()


class Particle(pygame.sprite.Sprite):
    def __init__(self, parent, pos, dx, dy):
        super().__init__(parent.particles_group)
        self.parent = parent
        self.image = choice(parent.fire)
        self.rect = self.image.get_rect()
        # у каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos
        # гравитация будет одинаковой
        self.gravity = 0.25

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect((0, 0, self.parent.WIDTH, self.parent.HEIGHT)):
            self.kill()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, parent):
        super().__init__(parent.tiles_group, parent.all_sprites)
        self.parent = parent
        self.image = parent.tile_images[tile_type]
        self.rect = self.image.get_rect().move(parent.tile_width * pos_x, parent.tile_height * pos_y)
        sprite = pygame.sprite.Sprite()
        sprite.image = self.image
        sprite.rect = self.rect
        parent.all_sprites.add(sprite)
        parent.tiles_group.add(sprite)
        parent.all_sprites.remove(list(parent.all_sprites)[-1])
        parent.tiles_group.remove(list(parent.tiles_group)[-1])


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, parent):
        super().__init__(parent.player_group, parent.all_sprites)
        self.parent = parent
        self.image = parent.player_image
        self.rect = self.image.get_rect().move(parent.tile_width * pos_x, parent.tile_height * pos_y)
        sprite = pygame.sprite.Sprite()
        sprite.image = self.image
        colorkey = self.image.get_at((0, 0))
        self.image.set_colorkey(colorkey)
        sprite.rect = self.rect
        parent.all_sprites.add(sprite)
        parent.player_group.add(sprite)
        parent.player_group.remove(list(parent.player_group)[-1])
        parent.all_sprites.remove(list(parent.all_sprites)[-1])


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, parent):
        self.dx, self.dy = parent.WIDTH // 2, parent.HEIGHT // 2
        self.parent = parent

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect = list(obj.rect)
        obj.rect[0] += self.dx
        obj.rect[1] += self.dy
        obj.rect = tuple(obj.rect)

    # позиционировать камеру на объекте target
    def update(self):
        self.dx = -(self.parent.player.rect[0] + self.parent.player.rect[2] // 2 - self.parent.WIDTH // 2)
        self.dy = -(self.parent.player.rect[1] + self.parent.player.rect[3] // 2 - self.parent.HEIGHT // 2)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, group):
        super().__init__(group)
        self.group = group
        self.jumping = False
        self.sheet = sheet
        self.columns = columns
        self.rows = rows
        self.x = x
        self.y = y
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x - self.rect[2], y - self.rect[3] + 5)
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame += 1
        self.image = self.frames[self.cur_frame % len(self.frames)]
        self.image.set_colorkey(self.image.get_at((0, 0)))
        if self.jumping and self.cur_frame == len(self.frames):
            self.jumping = False

            self.frames = []
            self.cut_sheet(self.sheet, self.columns, self.rows)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x - self.rect[2], self.y - self.rect[3] + 5)
            self.mask = pygame.mask.from_surface(self.image)
            # self.image.set_colorkey(self.image.get_at((0, 0)))
        if not self.jumping and pygame.key.get_pressed()[32]:
            self.jump()
        self.cur_frame = self.cur_frame % len(self.frames)

    def jump(self):
        super().__init__(self.group)
        self.jumping = True
        self.frames = []
        self.cut_sheet(load_image('dino-jump.png'), 7, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        # self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect = self.rect.move(self.x - self.rect[2], self.y - self.rect[3] + 5)
        self.mask = pygame.mask.from_surface(self.image)

    def is_jumping(self):
        return self.jumping


class WallForDino(pygame.sprite.Sprite):
    def __init__(self, parent, x):
        super().__init__(parent.walls_group, parent.all_spr)
        self.parent = parent
        self.image = load_image('kaktus.png')
        self.rect = self.image.get_rect().move(
            parent.parent.WIDTH + (x * self.image.get_rect()[2]), 300 - self.image.get_rect()[3]
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.image.set_colorkey(self.image.get_at((0, 0)))
        sprite = pygame.sprite.Sprite()
        sprite.image = self.image
        sprite.rect = self.rect
        parent.walls_group.add(sprite)


class Protection(pygame.sprite.Sprite):
    def __init__(self, parent, x):
        self.__class__.__name__ = 'Protection'
        self.parent = parent
        self.image = load_image('protect.png')
        self.rect = self.image.get_rect().move(
            parent.parent.WIDTH + (x * self.image.get_rect()[2]), 290 - self.image.get_rect()[3]
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.image.set_colorkey(self.image.get_at((0, 0)))
        sprite = pygame.sprite.Sprite()
        sprite.image = self.image
        sprite.rect = self.rect
        parent.all_spr.add(sprite)
        parent.protect_spr.add(sprite)


class GoogleDino:
    def __init__(self, parent):
        self.parent = parent
        self.win_game = None

        self.screen_size = self.screen_width, self.screen_height = 500, 500
        self.dino_screen = pygame.Surface(self.screen_size)

        self.fon = load_image('dino_fon.png')
        self.fon_x = 0
        self.dino_screen.blit(self.fon, (0, 135))

        self.dino_group = pygame.sprite.Group()
        self.walls_group = pygame.sprite.Group()
        self.all_spr = pygame.sprite.Group()
        self.protect_spr = pygame.sprite.Group()

        x_walls, x_protect = self.generate_kaktuses()
        for i in x_walls:
            WallForDino(self, i)
        for i in x_protect:
            Protection(self, i)

        self.dino = AnimatedSprite(load_image('dino-run.png'), 5, 1, self.screen_width // 7, 295, self.all_spr)
        self.dino_frame_per_game_frame = 0.5
        self.dino_jumping = False
        self.dino_group.add(self.dino)
        self.all_spr.add(self.dino)

        self.frame = 0

        self.dino_screen.fill((255, 255, 255))
        self.dino_screen.blit(self.fon, (self.fon_x, 135))
        self.dino.image.set_colorkey(self.dino.image.get_at((0, 0)))
        self.all_spr.draw(self.dino_screen)
        self.wall_move = -8
        self.score = 0

        self.font = pygame.font.Font(None, 30)
        string_rendered = self.font.render(str(self.score), 1, pygame.Color('black'))
        self.dino_screen.blit(string_rendered, (10, 10, 400, 20))
        self.running_game = True
        self.jumped = False
        self.protect_time = -1

    def generate_kaktuses(self):
        # list of kaktuses
        amount = choice([_ for _ in range(10, 25)])
        ooo = [_ for _ in range(1, 15)]
        sp = [choice(ooo)]
        for i in range(amount):
            sp.append(sp[-1] + choice(ooo))
        sp_1 = sp[:]
        for _ in range(3):
            for i in range(len(sp)):
                try:
                    a = sp[i:i + 3]
                    if 0 < a[1] - a[0] == a[2] - a[1] and a[1] - a[0] < 7:
                        sp_1.remove(sp[i])
                    elif 1 < a[1] - a[0] < 7:
                        sp_1.remove(sp[i])
                except Exception:
                    pass
            sp = sp_1[::]

        # list of protection (щитов)
        amount = choice([_ for _ in range(5)])
        ooo = [_ for _ in range(15, 60)]
        spis = [choice(ooo)]
        for i in range(amount):
            a = spis[-1] + choice(ooo)
            if a >= sp[-1]:
                break
            elif a in sp:
                continue
            spis.append(a)

        return sp, spis

    def status(self):
        return self.running_game, self.win_game

    def update(self):
        if len(self.walls_group) == 0:
            text = self.font.render('You WIN!', False, pygame.Color('orange'))
            self.win_game = True
            self.dino_screen.blit(text, (200, 320, 500, 500))
            self.score += 100
            self.running_game = False
            return self.dino_screen
        self.dino_screen.fill((255, 255, 255))
        if not self.jumped:
            string = self.font.render("Нажмите 'пробел' для прыжка", False, pygame.Color('black'))
            self.dino_screen.blit(string, (10, 400, 400, 20))

        self.frame += 1
        self.dino_jumping = self.dino.is_jumping()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.dino_jumping:
                    self.dino.jump()
                    self.jumped = True
                elif event.key == pygame.K_ESCAPE:
                    self.parent.dino_is_active = False
                elif event.key == pygame.K_q:
                    # отладочная клавиша, никому об этом не говори
                    self.win_game = True
                    self.running_game = False

        for wall in self.walls_group:
            o = wall.rect
            if o[0] < - o[2]:
                self.walls_group.remove(wall)
                self.all_spr.remove(wall)
            wall.rect = wall.rect.move(self.wall_move, 0)

        for pr in self.protect_spr:
            o = pr.rect
            if o[0] < 55:
                self.protect_spr.remove(pr)
                self.all_spr.remove(pr)
            pr.rect = pr.rect.move(self.wall_move, 0)
        self.dino_screen.blit(self.fon, (self.fon_x, 135))

        if self.dino_jumping:
            self.dino_frame_per_game_frame = 0.35
            self.score += 0.05
        else:
            self.dino_frame_per_game_frame = 0.7
            self.score += 0.05
        string_rendered = self.font.render(str(int(self.score)), 1, pygame.Color('black'))
        self.dino_screen.blit(string_rendered, (10, 10, 400, 20))

        if self.frame * self.dino_frame_per_game_frame >= 1:
            self.dino.update()
            self.frame = 0
        self.dino.image.set_colorkey(self.dino.image.get_at((0, 0)))

        self.all_spr.draw(self.dino_screen)
        self.parent.main_screen.blit(self.dino_screen, self.parent.dino_rect)

        self.dino.mask = pygame.mask.from_surface(self.dino.image)

        for i in self.protect_spr:
            i.mask = pygame.mask.from_surface(i.image)
            if pygame.sprite.collide_mask(self.dino, i) is not None:
                self.protect_time = 100
                break
        if self.protect_time <= 0:
            if self.protect_time == 0:
                try:
                    a = self.protect_spr.sprites()[-1]
                    self.protect_spr.remove(a)
                    self.all_spr.remove(a)
                except Exception:
                    pass
                self.protect_time = -1
            for i in self.walls_group:
                i.mask = pygame.mask.from_surface(i.image)
                if pygame.sprite.collide_mask(self.dino, i) is not None:
                    text = self.font.render('You lose', False, pygame.Color('black'))
                    self.win_game = False
                    self.dino_screen.blit(text, (200, 320, 500, 500))
                    self.running_game = False
                    for w in self.walls_group:
                        w.rect = w.image.get_rect().move(-1 * (self.parent.WIDTH + 100), 0)
                    break
        else:
            try:
                a = self.protect_spr.sprites()[-1]
                self.protect_spr.remove(a)
                self.all_spr.remove(a)
            except Exception:
                pass
            a = Protection(self, -21)
            self.protect_spr.remove(a)
            self.protect_time -= 1

        return self.dino_screen


if __name__ == "__main__":
    pygame.init()
    main_game = MainGame()
    main_game.start()
