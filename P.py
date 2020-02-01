import pygame
import os
import sys
from random import random, sample, choice
from math import e


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if colorkey is not None:
        image = pygame.image.load(fullname).convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = pygame.image.load(fullname).convert()
    return image


def terminate():
    pygame.quit()
    sys.exit()


class MainGame:
    def __init__(self):
        self.lvl_width = None
        self.lvl_height = None
        self.lvl_map = [['@']]
        self.difficulty = 0

        self.load_random_lvl()
        self.WIDTH = 500
        self.HEIGHT = 500
        self.SIZE = (self.WIDTH, self.HEIGHT)
        self.font = pygame.font.Font(None, 30)

        self.clock = pygame.time.Clock()
        self.FPS = 50
        self.dino_FPS = 30

        self.running = True
        self.main_screen = pygame.display.set_mode(self.SIZE)
        self.main_screen.fill((0, 0, 0))

        self.tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
        self.player_image = load_image('mario.png')

        self.tile_width = 50
        self.tile_height = 50

        self.player = None
        self.p_x = 0
        self.p_y = 0

        self.all_sprites = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

        self.dino_is_active = False

    def load_level(self, f_name):
        fname = "data/" + f_name
        try:
            with open(fname, 'r') as mapFile:
                level_map = [line.strip() for line in mapFile]
            max_width = max(map(len, level_map))
            self.lvl_map = list(map(list, map(lambda x: x.ljust(max_width, '.'), level_map)))
        except FileNotFoundError:
            print(f"Файл '{f_name}' не найден")
            terminate()

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
            # print(''.join(map(str, range(self.lvl_width))))
            # print('\n'.join([str(i) + ":\t" + ''.join(row) for i, row in enumerate(self.lvl_map)]))
            # print(count)
            # print()
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

        # y = randrange(6, self.lvl_height, 2)
        # x = randrange(1, self.lvl_width, 2)
        # self.lvl_map[y][x] = "$"  # это у нас будет выходом, который перемещает нас на след. уровень

    def start(self):
        intro_text = ['Hello!', 'There are some rules!', 'JOKE', "We have no rules"]

        background = pygame.transform.scale(load_image('fon.jpg'), self.SIZE)
        self.main_screen.blit(background, (0, 0))
        text_coord = 50
        for line in intro_text:
            string_rendered = self.font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.main_screen.blit(string_rendered, intro_rect)

        while True:
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
                and self.lvl_map[self.p_y + dy][self.p_x + dx] == '.'
        ):
            self.lvl_map[self.p_y][self.p_x] = '.'
            self.lvl_map[self.p_y + dy][self.p_x + dx] = '@'
            self.p_x += dx
            self.p_y += dy
            self.player.rect = (
                self.player.rect[0] + dx * self.tile_width, self.player.rect[1] + dy * self.tile_height,
                self.player.rect[2], self.player.rect[3]
            )

    def main_gameplay(self):
        self.generate_level()
        camera = Camera(self)
        while True:
            if self.dino_is_active:
                self.main_screen.blit(self.dino_game.update(), self.dino_rect)
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
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
                        elif event.key == pygame.K_SPACE:
                            self.dino_is_active = True
                            self.dino_game = GoogleDino(self)
                            self.dino_rect = pygame.Rect(0, 0, 500, 500)
                # изменяем ракурс камеры
                camera.update()
                # обновляем положение всех спрайтов
                for sprite in self.all_sprites:
                    camera.apply(sprite)
                self.main_screen.fill((0, 0, 0))
                self.tiles_group.draw(self.main_screen)
                self.player_group.draw(self.main_screen)
            pygame.display.flip()
            if self.dino_is_active:
                self.clock.tick(self.dino_FPS)
            else:
                self.clock.tick(self.FPS)

    def generate_level(self):
        self.lvl_width = len(self.lvl_map[0])
        self.lvl_height = len(self.lvl_map)
        for y in range(self.lvl_height):
            for x, cell in enumerate(self.lvl_map[y]):
                if cell == '.':
                    Tile('empty', x, y, self)
                elif cell == '#':
                    Tile('wall', x, y, self)
                elif cell == '@':
                    Tile('empty', x, y, self)
                    self.player = Player(x, y, self)
                    self.p_x = x
                    self.p_y = y
        self.all_sprites.draw(self.main_screen)


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
        self.rect = self.rect.move(x - self.rect[2], y - self.rect[3])

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
            self.rect = self.rect.move(self.x - self.rect[2], self.y - self.rect[3])
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
        self.rect = self.rect.move(self.x - self.rect[2], self.y - self.rect[3])

    def is_jumping(self):
        return self.jumping


class WallForDino(pygame.sprite.Sprite):
    def __init__(self, parent, x):
        super().__init__(parent.walls_group, parent.all_spr)
        self.parent = parent
        self.image = load_image('kaktus.png')
        self.rect = self.image.get_rect().move(
            main_game.WIDTH + x * self.image.get_rect()[2], 300 - self.image.get_rect()[3]
        )
        sprite = pygame.sprite.Sprite()
        sprite.image = self.image
        self.image.set_colorkey(self.image.get_at((0, 0)))
        sprite.rect = self.rect
        parent.walls_group.add(sprite)


class GoogleDino:
    def __init__(self, parent):
        self.parent = parent

        self.screen_size = self.screen_width, self.screen_height = 500, 500
        self.dino_screen = pygame.Surface(self.screen_size)

        self.fon = load_image('dino_fon.png')
        self.fon_x = 0
        self.dino_screen.blit(self.fon, (0, 135))

        self.dino_group = pygame.sprite.Group()
        self.walls_group = pygame.sprite.Group()
        self.all_spr = pygame.sprite.Group()

        x_walls = self.generate_kaktuses()
        print(x_walls)
        for i in x_walls:
            _ = WallForDino(self, i)

        self.dino = AnimatedSprite(load_image('dino-run.png'), 5, 1, self.screen_width // 7, 303, self.all_spr)
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

    def generate_kaktuses(self):
        amount = choice([_ for _ in range(100, 1000)])
        ooo = [_ for _ in range(1, 10)]
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
                    elif 1 < a[1] - a[0] < 6:
                        sp_1.remove(sp[i])
                except Exception:
                    pass
            sp = sp_1[::]
        return sp

    def update(self):
        self.frame += 1
        self.dino_jumping = self.dino.is_jumping()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.dino_jumping:
                    self.dino.jump()
                elif event.key == pygame.K_ESCAPE:
                    self.parent.dino_is_active = False
        self.dino_screen.fill((255, 255, 255))

        for wall in self.walls_group:
            o = wall.rect
            if o[0] < - o[2]:
                self.walls_group.remove(wall)
            wall.rect = wall.image.get_rect().move(wall.rect[0] + self.wall_move, wall.rect[1])
        self.dino_screen.blit(self.fon, (self.fon_x, 135))

        if self.dino_jumping:
            self.dino_frame_per_game_frame = 0.35
        else:
            self.dino_frame_per_game_frame = 0.7

        if self.frame * self.dino_frame_per_game_frame >= 1:
            self.dino.update()
            self.frame = 0
        self.dino.image.set_colorkey(self.dino.image.get_at((0, 0)))

        self.dino_group.draw(self.dino_screen)
        self.walls_group.draw(self.dino_screen)
        return self.dino_screen


if __name__ == "__main__":
    pygame.init()
    main_game = MainGame()
    main_game.start()
