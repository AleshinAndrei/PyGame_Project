import pygame
import sys
from random import random, sample, choice, randrange
from .dino import GoogleDino
from .camera import Camera
from .tile import Tile
from .player import Player
from .particle import Particle
from .load_image import load_image


GENERATE_PARTICLE = randrange(25, 32)


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
        self.timer = 80 * self.FPS

        self.running = True
        self.main_screen = pygame.display.set_mode(self.SIZE)
        self.main_screen.fill((0, 0, 0))

        self.tile_images = {'wall': load_image('wall.png'), 'empty': load_image('ground.png')}
        cup_image = load_image('ground.png')
        cup_image.blit(load_image("cup.png"), (5, 5))
        self.tile_images['cup'] = cup_image
        self.background = pygame.transform.scale(load_image('fon.jpg'), self.SIZE)

        self.player_image = load_image('mario.png')

        self.tile_width = 50
        self.tile_height = 50

        self.player = None
        self.p_x = 0
        self.p_y = 0
        self.player_name = ""

        self.all_sprites = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.particles_group = pygame.sprite.Group()

        self.new_dino_game()
        self.dino_is_active = False
        self.win_dino_game = True

        self.win_main_game = False

        # сгенерируем частицы разного размера
        self.fire = [load_image("star.png", -1)]
        for scale in (5, 10, 20):
            self.fire.append(pygame.transform.scale(self.fire[0], (scale, scale)))

    def load_random_lvl(self):
        """Loading random level. Using internal parameters of difficulty, size of map, etc."""
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
                        if random() > 2 / (1 + 2 ** (-self.difficulty * 0.3)) - 1 or new_branch:
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

    def render_top5(self):
        """Rendering TOP5 banner on the Home page in the right upper corner"""
        with open("records", "r") as file:
            records = list(map(lambda line:
                               (line.strip().split('\t')[0],
                                int(line.strip().split('\t')[1])),
                               file.readlines()))
            top5_rendered = self.font.render("Top 5:", 1, pygame.Color('gold'))
            top5_rect = top5_rendered.get_rect()  # center=(self.WIDTH - 200, 10)
            y_coord = 10
            top5_rect.top = y_coord
            top5_rect.x = self.WIDTH - 210
            y_coord += top5_rect.height + 10
            self.main_screen.blit(top5_rendered, top5_rect)
            for name, time in records[:5]:
                name_rendered = self.font.render(name, 1, pygame.Color('gold'))
                name_rect = name_rendered.get_rect()
                name_rect.top = y_coord
                name_rect.x = self.WIDTH - 210
                self.main_screen.blit(name_rendered, name_rect)

                time_rendered = self.font.render(
                    f'{time // 60}:{time % 60:0>2}',
                    1, pygame.Color('gold')
                )
                time_rect = time_rendered.get_rect()
                time_rect.top = y_coord
                time_rect.x = self.WIDTH - time_rect.width - 2
                self.main_screen.blit(time_rendered, time_rect)

                y_coord += name_rect.height + 10

    def render_intro(self):
        """Rendering intro words on the Home page"""
        intro_text = ['New Game', "Find the Cup", "Press 'space' to start"]
        text_coord = 115
        for line in intro_text:
            string_rendered = self.font.render(line, 1, pygame.Color('gold'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.main_screen.blit(string_rendered, intro_rect)

        string_rendered = self.font.render('Created by Aleshin Andrei and Grishina Lena', 1, pygame.Color('gold'))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = 10
        intro_rect.top = 475
        self.main_screen.blit(string_rendered, intro_rect)

    def start(self):
        """Starting the Game"""
        self.player_name = ""
        self.main_screen.blit(self.background, (0, 0))

        self.render_top5()
        self.render_intro()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.entering_name()
                    self.main_gameplay()
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def render_entering(self):
        """Rendering the entering a nickname"""
        text = "Enter the name:"
        text_rendered = self.font.render(text, 2, pygame.Color("yellow"))
        name_rendered = self.font.render(self.player_name, 2, pygame.Color("green"))
        text_rect = text_rendered.get_rect()
        name_rect = name_rendered.get_rect()
        text_rect.top = 80
        text_rect.x = 160
        name_rect.top = 100
        name_rect.x = 160
        self.main_screen.blit(self.background, (0, 0))
        self.main_screen.blit(text_rendered, text_rect)
        self.main_screen.blit(name_rendered, name_rect)

    def entering_name(self):
        """Entering a nickname to records table"""
        self.main_screen.blit(self.background, (0, 0))

        entering = True
        while entering:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        entering = False
                    elif event.key == pygame.K_BACKSPACE:
                        if self.player_name:
                            self.player_name = self.player_name[:-1]
                        print(self.player_name)
                    else:
                        if len(self.player_name) < 16:
                            self.player_name += event.unicode
            self.render_entering()
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
                    self.win_main_game = True
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
        """Starting DinoGame during MainGame"""
        self.dino_rect = pygame.Rect(0, 0, 500, 500)
        self.dino_is_active = True
        self.win_dino_game = False
        self.dino_game = GoogleDino(self)

    def render_main_gameplay(self, timer):
        """Rendering MainGame"""
        self.main_screen.fill((0, 0, 0))
        self.tiles_group.draw(self.main_screen)
        self.player_group.draw(self.main_screen)

        find_cup_rendered = self.font.render("Find the CUP", 2, pygame.Color('gold'))
        find_cup_rect = find_cup_rendered.get_rect()
        find_cup_rect.top = 12
        find_cup_rect.x = 80
        self.main_screen.blit(find_cup_rendered, find_cup_rect)

        timer_string = "Remaining time: "
        timer_string += str(timer // self.FPS)
        if timer < self.timer // 3:
            timer_color = "red"
        elif timer < 2 * self.timer // 3:
            timer_color = "goldenrod1"
        else:
            timer_color = "seagreen1"
        timer_rendered = self.font.render(timer_string, 2, pygame.Color(timer_color))
        timer_rect = timer_rendered.get_rect()
        timer_rect.top = 12
        timer_rect.x = 250
        self.main_screen.blit(timer_rendered, timer_rect)

    def main_gameplay(self):
        """Processing MainGameplay"""
        self.rendering_level()
        camera = Camera(self)
        timer = self.timer
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
                self.render_main_gameplay(timer)

            pygame.display.flip()
            if self.dino_is_active:
                self.clock.tick(self.dino_FPS)
            else:
                self.clock.tick(self.FPS)
                timer -= 1
                if timer == 0:
                    self.running = False

        if self.win_main_game:
            self.game_end_with_win(self.timer - timer)
        else:
            self.game_end_with_lose()

    def rendering_level(self):
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

    def game_end_with_lose(self):
        """Processing end of game with lose"""
        text = 'You Lose!!'
        string_rendered = self.font.render(text, 1, pygame.Color('red3'))
        text_rect = string_rendered.get_rect()
        text_rect.x = 200
        text_rect.top = 200
        timer = 7 * self.FPS

        escape = False
        while (not escape) and timer:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                    terminate()
                if event.type == pygame.KEYUP:
                    escape = True
                    break
            timer -= 1

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

    def game_end_with_win(self, time):
        """Processing end of game with win"""
        count = 6

        particle_count = choice(list(range(20, 40)))
        numbers = range(-5, 6)

        win_text = ['You Win!!',
                    f'Time {(time // self.FPS) // 60}:{(time // self.FPS) % 60:0>2}',
                    'Press Esc to Exit']
        text_coord = 115
        with open("records", "r+") as file:
            records = list(map(lambda line:
                               (line.strip().split('\t')[0],
                                int(line.strip().split('\t')[1])),
                               file.readlines()))
            records.append((self.player_name, time // self.FPS))
            records.sort(key=lambda x: x[1])
            file.seek(0)
            file.write('\n'.join(map(lambda line: line[0] + '\t' + str(line[1]), records)))

        lines_rendered = []
        lines_rect = []
        for line in win_text:
            lines_rendered.append(self.font.render(line, 1, pygame.Color('yellow')))
            lines_rect.append(lines_rendered[-1].get_rect(center=(self.WIDTH / 2, text_coord)))
            text_coord += lines_rect[-1].height
            self.main_screen.blit(lines_rendered[-1], lines_rect[-1])

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

            for i in range(len(lines_rendered)):
                self.main_screen.blit(lines_rendered[i], lines_rect[i])
            pygame.display.flip()
            self.clock.tick(self.FPS)

        global main_game
        main_game = MainGame()
        main_game.start()
