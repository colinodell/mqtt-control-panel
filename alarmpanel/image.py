import pygame

class Image:
    def __init__(self, path, name):
        self.name = name
        try:
            self.bitmap = pygame.image.load(path + '/' + name + '.png')
        except:
            pass