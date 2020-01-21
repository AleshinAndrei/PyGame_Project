import pygame
import os
import sys
import random


class MainGame:
    def __init__(self):
        self.lvl_map = [['@']]
        self.load_level(input("Введите название файла с уровнем в формате '*название*.txt' "))
        self.WIDTH = 500
        self.HEIGHT = 500
        self.SIZE = (self.WIDTH, self.HEIGHT)
        self.font = pygame.font.Font(None, 30)

        self.clock = pygame.time.Clock()
        self.FPS = 50

        self.running = True
        self.main_screen = pygame.display.set_mode(self.SIZE)
        self.main_screen.fill((0, 0, 0))

        self.tile_images = {'wall': self.load_image('box.png'), 'empty': self.load_image('grass.png')}
        self.player_image = self.load_image('mario.png')

        self.tile_width = 50
        self.tile_height = 50

        self.player = None
        self.p_x = 0
        self.p_y = 0

        self.lvl_width = None
        self.lvl_height = None

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

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('data', name)
        if colorkey is not None:
            image = pygame.image.load(fullname).convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = pygame.image.load(fullname).convert()
        return image

    def start(self):
        intro_text = ['Hello!', 'There are some rules!', 'JOKE', "We have no rules"]

        background = pygame.transform.scale(self.load_image('fon.jpg'), self.SIZE)
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
                        pass
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


def terminate():
    pygame.quit()
    sys.exit()


"""
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
"""


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
        super().__init__(self.parent.all_sprites)
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


if __name__ == "__main__":
    pygame.init()
    main_game = MainGame()
    main_game.start()
