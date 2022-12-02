import pygame
from .load_image import load_image
from random import choice
import sys


def terminate():
    pygame.quit()
    sys.exit()


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
