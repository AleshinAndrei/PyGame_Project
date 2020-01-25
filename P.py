import pygame
import os
import sys
from random import randrange, random, sample
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

    def load_level(self, f_name):
        fname = "data/" + f_name
        try:
            with open(fname, 'r') as mapFile:
                level_map = [line.strip() for line in mapFile]
            max_width = max(map(len, level_map))
            self.lvl_map = list(map(list, map(lambda x: x.ljust(max_width, '.'), level_map)))
        except FileNotFoundError:
            print(f"Файл '{f_name}' не найден")

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
                        dino_play = GoogleDino(self.main_screen)
                        # тут должен быть динозаврик
            # изменяем ракурс камеры
            camera.update()
            # обновляем положение всех спрайтов
            for sprite in self.all_sprites:
                camera.apply(sprite)
            self.main_screen.fill((0, 0, 0))
            self.tiles_group.draw(self.main_screen)
            self.player_group.draw(self.main_screen)
            pygame.display.flip()
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
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(main_game.all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        # self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.image.set_colorkey(self.image.get_at((0, 0)))


class WallForDino(pygame.sprite.Sprite):
    def __init__(self, parent):
        super().__init__(parent.player_group, parent.all_sprites)
        self.parent = parent
        self.wall_image = load_image('kaktus.png')
        self.wall_rect = self.wall_image.get_rect().move(0, 0)
        sprite = pygame.sprite.Sprite()
        sprite.image = self.wall_image
        self.wall_image.set_colorkey(self.wall_image.get_at((0, 0)))
        sprite.rect = self.wall_image
        parent.wall_sprite.add(sprite)
        parent.wall_sprite.draw(main_game.main_screen)


class GoogleDino:
    def __init__(self, screen):
        screen.fill((255, 255, 255))
        self.fon = load_image('dino_fon.png')
        self.fon_x = 0
        screen.blit(self.fon, (0, 135))
        pygame.display.flip()
        self.dino_group = pygame.sprite.Group()
        walls_group = []
        self.dino = AnimatedSprite(load_image('dino-run.png'), 5, 1, 0, 0)
        self.dino.rect = self.dino.rect.move(main_game.WIDTH // 15, 245)
        self.dino_group.add(self.dino)
        self.screen = screen

        self.screen.fill((255, 255, 255))
        self.screen.blit(self.fon, (self.fon_x, 135))
        self.dino.update()
        self.dino.image.set_colorkey(self.dino.image.get_at((0, 0)))
        self.dino_group.draw(self.screen)
        pygame.display.flip()

        self.play()

        ''' 
        self.score = 0
        self.wall_list = []
        self.hero_run = AnimatedSprite(load_image('dino-run.png'), 5, 1, 63, 70)
        self.hero_jump = AnimatedSprite(load_image('dino-jump.png'), 5, 1, 63, 100)
        self.hero_x_right = main_game.WIDTH // 15
        '''

    def play(self):
        playing = True
        while playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == 32:  # space
                        pass
                    elif event.key == 27:  # esc  => break the mini-game
                        playing = False
            self.screen.fill((255, 255, 255))
            a = main_game.clock.tick()
            self.screen.blit(self.fon, (self.fon_x, 135))
            self.dino.update()
            self.dino.image.set_colorkey(self.dino.image.get_at((0, 0)))
            self.dino_group.draw(self.screen)
            pygame.display.flip()
            main_game.clock.tick(15)


if __name__ == "__main__":
    pygame.init()
    main_game = MainGame()
    main_game.start()
