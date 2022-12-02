import pygame
from random import choice


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
