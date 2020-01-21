import pygame
import os
import sys
import random

lev = input("Введите название файла с уровнем в формате '*название*.txt' ")


def terminate():
    pygame.quit()
    sys.exit()


def load_level(f_name):
    filename = "data/" + f_name
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))
    except FileNotFoundError:
        print("Файл '{}' не найден".format(f_name))
        terminate()


a = load_level(lev)
pygame.init()
size = WIDTH, HEIGHT = 500, 500
running = True
screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))
clock = pygame.time.Clock()
FPS = 50
walls_for_dino = ['']


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    return image


def generate_level(level):
    global all_sprites, tiles_group, player_group
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    all_sprites.draw(screen)
    return new_player, x, y


def start_screen():
    intro_text = ['Hello!', 'There are some rules!', 'JOKE', "We have no rules"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                level(lev)
        pygame.display.flip()
        clock.tick(FPS)


def level(lev):
    global player
    a = load_level(lev)
    player, level_x, level_y = generate_level(a)
    x, y = list(player.rect)[:2]
    p_x = x // 50
    p_y = y // 50
    camera = Camera()
    for i in range(len(a)):
        a[i] = list(a[i])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == 273:  # up
                    if p_y != 0 and a[p_y - 1][p_x] == '.':
                        a[p_y][p_x] = '.'
                        a[p_y - 1][p_x] = '@'
                        p_y -= 1
                        player.rect = (player.rect[0], player.rect[1] - 50, player.rect[2], player.rect[3])
                elif event.key == 274:  # down
                    if p_y < level_y and a[p_y + 1][p_x] == '.':
                        a[p_y][p_x] = '.'
                        a[p_y + 1][p_x] = '@'
                        p_y += 1
                        player.rect = (player.rect[0], player.rect[1] + 50, player.rect[2], player.rect[3])
                elif event.key == 275:  # right
                    if p_x < level_x and a[p_y][p_x + 1] == '.':
                        a[p_y][p_x] = '.'
                        a[p_y][p_x + 1] = '@'
                        p_x += 1
                        player.rect = (player.rect[0] + 50, player.rect[1], player.rect[2], player.rect[3])
                elif event.key == 276:  # left
                    if p_x != 0 and a[p_y][p_x - 1] == '.':
                        a[p_y][p_x] = '.'
                        a[p_y][p_x - 1] = '@'
                        p_x -= 1
                        player.rect = (player.rect[0] - 50, player.rect[1], player.rect[2], player.rect[3])
                elif event.key == 32:
                    play_dino()
        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill((0, 0, 0))
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def play_dino():
    screen.fill((255, 255, 255))
    fon = load_image('dino_fon.png')
    fon_x = 0
    screen.blit(fon, (0, 135))
    pygame.display.flip()
    dino_group = pygame.sprite.Group()
    walls_group = []
    dino = AnimatedSprite(load_image('dino-run.png'), 5, 1, 0, 0)
    dino.rect = dino.rect.move(WIDTH // 15, 245)
    dino_group.add(dino)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == 32:  # space
                    pass
        screen.fill((255, 255, 255))
        a = clock.tick()
        screen.blit(fon, (fon_x, 135))
        dino.update()
        dino.image.set_colorkey(dino.image.get_at((0, 0)))
        dino_group.draw(screen)
        pygame.display.flip()
        clock.tick(15)


player = None

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
player_image = load_image('mario.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        sprite = pygame.sprite.Sprite()
        sprite.image = self.image
        sprite.rect = self.rect
        all_sprites.add(sprite)
        tiles_group.add(sprite)
        all_sprites.remove(list(all_sprites)[-1])
        tiles_group.remove(list(tiles_group)[-1])


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        sprite = pygame.sprite.Sprite()
        sprite.image = self.image
        colorkey = self.image.get_at((0, 0))
        self.image.set_colorkey(colorkey)
        sprite.rect = self.rect
        all_sprites.add(sprite)
        player_group.add(sprite)
        player_group.remove(list(player_group)[-1])
        all_sprites.remove(list(all_sprites)[-1])


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx, self.dy = WIDTH // 2, HEIGHT // 2

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect = list(obj.rect)
        obj.rect[0] += self.dx
        obj.rect[1] += self.dy
        obj.rect = tuple(obj.rect)

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect[0] + target.rect[2] // 2 - WIDTH // 2)
        self.dy = -(target.rect[1] + target.rect[3] // 2 - HEIGHT // 2)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
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


class WallForDino:
    def __init__(self):
        pass


'''
class GoogleDino:
    def __init__(self):
        self.score = 0
        self.wall_list = []
        self.hero_run = AnimatedSprite(load_image('dino-run.png'), 5, 1, 63, 70)
        self.hero_jump = AnimatedSprite(load_image('dino-jump.png'), 5, 1, 63, 100)
        self.hero_x_right = WIDTH // 15

    def play(self):
        pass
'''


start_screen()
