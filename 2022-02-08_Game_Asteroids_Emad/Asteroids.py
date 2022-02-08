from tracemalloc import stop
from turtle import position
import pygame
from pygame.constants import (QUIT, KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE, K_ESCAPE)
import os



class Settings(object):
    window = {'width':800, 'height':500}
    fps = 60
    title = "Asteroids"
    path = {}
    path['file'] = os.path.dirname(os.path.abspath(__file__))
    path['image'] = os.path.join(path['file'], "images")
    directions = {'stop':(0, 0), 'down':(0,  1), 'up':(0, -1), 'left':(-1, 0), 'right':(1, 0)}

    def dim():
        return (Settings.window['width'], Settings.window['height'])

    @staticmethod
    def filepath(name):
        return os.path.join(Settings.path['file'], name)

    @staticmethod
    def imagepath(name):
        return os.path.join(Settings.path['image'], name)


class Timer(object):
    def __init__(self, duration, with_start = True):
        self.duration = duration
        if with_start:
            self.next = pygame.time.get_ticks()
        else:
            self.next = pygame.time.get_ticks() + self.duration

    def is_next_stop_reached(self):
        if pygame.time.get_ticks() > self.next:
            self.next = pygame.time.get_ticks() + self.duration
            return True
        return False

    def change_duration(self, delta=10):
        self.duration += delta
        if self.duration < 0:
            self.duration = 0

class Raumschiff(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_orig=pygame.image.load(Settings.imagepath("raumschiff.png")).convert()
        self.image_orig = pygame.transform.scale(self.image_orig,(50, 38))
        self.image=self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (Settings.window['width'] // 2, Settings.window['height'] // 2)
        self.animation_time = Timer(100)
        self.scale = {'width': self.rect.width, 'height': self.rect.height}
        self.rot= 0         # for rotate

    def update(self):
        position = self.rect.center        # remember old center
        self.rect = self.image.get_rect()
        self.rect.center = position        # set center to old position

        self.rect.y -=1                     # just for testing
        self.rect.x +=1                     # just for testing
        if self.rect.left > Settings.window['width']:
            self.rect.right = 0
        if self.rect.right < 0:
            self.rect.left = Settings.window['width']
        if self.rect.bottom > Settings.window['height'] +38:
            self.rect.top = -38
        if self.rect.top < -38 :
            self.rect.bottom = Settings.window['height'] +38
    def l_rotate(self):
        self.grad= 22.5
        self.rot= self.rot + self.grad
        self.image= pygame.transform.rotate(self.image_orig, self.rot)

    def r_rotate(self):
        self.grad= 22.5
        self.rot= self.rot + self.grad * -1
        self.image= pygame.transform.rotate(self.image_orig, self.rot)

class Game(object):
    def __init__(self) -> None:
        super().__init__()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "10, 50"
        pygame.init()
        self.screen = pygame.display.set_mode(Settings.dim())
        pygame.display.set_caption(Settings.title)
        self.clock = pygame.time.Clock()

        self.raumschiff = pygame.sprite.GroupSingle(Raumschiff())
        
        self.running = False
        
    def watch_for_events(self):
        """Reaction of keyboard and other system events events.
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_LEFT:
                    self.raumschiff.sprite.l_rotate()
                elif event.key == K_RIGHT:
                    self.raumschiff.sprite.r_rotate()


    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        self.raumschiff.draw(self.screen)
        pygame.display.flip()

    def update(self) -> None:
        self.raumschiff.update()


    def run(self):
        """Starting point of the game.

        Call this method in order to start the game. It contains the main loop.
        """
        self.running = True
        while self.running:
            self.clock.tick(Settings.fps)
            self.watch_for_events()
            self.update()
            self.draw()


        pygame.quit()



if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = "10, 30"
    game = Game()
    game.run()
