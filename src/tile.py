import pygame


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
