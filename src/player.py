import pygame


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
