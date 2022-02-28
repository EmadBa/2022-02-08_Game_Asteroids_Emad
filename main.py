import pygame
import random
from pygame.math import Vector2
from pygame.transform import rotozoom
from pygame.constants import (QUIT, KEYDOWN, K_KP_ENTER, K_ESCAPE, K_RETURN)
import os


class Settings(object):
    window = {'width':800, 'height':500}
    fps = 60
    title = "Asteroids"
    path = {}
    path['file'] = os.path.dirname(os.path.abspath(__file__))
    path['image'] = os.path.join(path['file'], "images")

    UP = Vector2(0, -1)

    def get_windowsize():
        return (Settings.window['width'], Settings.window['height'])

    def filepath(name):
        return os.path.join(Settings.path['file'], name)

    def imagepath(name):
        return os.path.join(Settings.path['image'], name)

    def wrap_position(position, surface):
        x, y = position
        w, h = surface.get_size()
        return Vector2(x % w, y % h)
    
    def get_random_position(surface):
        return Vector2(random.randrange(surface.get_width()),random.randrange(surface.get_height()),)

    def get_random_velocity(min_speed, max_speed):
        speed = random.randint(min_speed, max_speed)
        angle = random.randrange(0, 360)
        return Vector2(speed, 0).rotate(angle)


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

class Gameobject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface):
        self.position = Settings.wrap_position(self.position + self.velocity, surface)

    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius


class Spaceship(Gameobject):

    move_speed = 0.1
    rotate_speed = 2.15
    bullet_speed = 3

    def __init__(self, position,create_bullet_callback):
        self.create_bullet_callback = create_bullet_callback
        super().__init__(position, pygame.image.load(Settings.imagepath("raumschiff.png")).convert_alpha(), Vector2(0))
        self.direction = Vector2(Settings.UP)
    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.rotate_speed * sign
        self.direction.rotate_ip(angle)

    def draw(self, surface):
        angle = self.direction.angle_to(Settings.UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)
    def accelerate(self):
        self.velocity += self.direction * self.move_speed

    def shoot(self):
        bullet_velocity = self.direction * self.bullet_speed + self.velocity
        bullet = Bullet(self.position, bullet_velocity)
        self.create_bullet_callback(bullet)


class Bullet(Gameobject):
    def __init__(self, position, velocity):
        super().__init__(position, pygame.image.load(Settings.imagepath("bullet.png")), velocity)
    def move(self, surface):
        self.position = self.position + self.velocity

class Asteroid(Gameobject):
    def __init__(self, position):
        super().__init__(position, pygame.image.load(Settings.imagepath("rock3.png")).convert_alpha(), Settings.get_random_velocity(1, 3))

class Game(object):
    def __init__(self) -> None:
        super().__init__()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "10, 50"
        pygame.init()
        self.screen = pygame.display.set_mode(Settings.get_windowsize())
        pygame.display.set_caption(Settings.title)
        self.clock = pygame.time.Clock()
        self.distance=250
        self.time= Timer(3000)
        self.bullets = []
        self.spaceship = Spaceship((400, 300),self.bullets.append)
        self.asteroids = []
        
    def get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets]
        if self.spaceship:
            game_objects.append(self.spaceship)
        return game_objects
        
    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:  
                if event.key == K_ESCAPE:
                    self.running = False
                if event.key == K_KP_ENTER or event.key==K_RETURN:
                    if len(self.bullets) <10:
                        self.spaceship.shoot()
            
        is_key_pressed = pygame.key.get_pressed()
        if is_key_pressed[pygame.K_RIGHT]:
            self.spaceship.rotate(clockwise=True)
        elif is_key_pressed[pygame.K_LEFT]:
            self.spaceship.rotate(clockwise=False)
        if is_key_pressed[pygame.K_UP]:
            self.spaceship.accelerate()

    def  draw(self):
        self.screen.fill((0, 0, 0))
        for object in self.get_game_objects():
            object.draw(self.screen)
        pygame.display.flip()

    def update(self) -> None:

        for object in self.get_game_objects():
            object.move(self.screen)
        for asteroid in self.asteroids:
            if asteroid.collides_with(self.spaceship):
                self.running = False
                break

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if asteroid.collides_with(bullet):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    break

        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

        if len(self.asteroids) <5:
            if self.time.is_next_stop_reached():
                while True:
                    position = Settings.get_random_position(self.screen)
                    if (position.distance_to(self.spaceship.position)> self.distance):
                        break
                self.asteroids.append(Asteroid(position))

    

    def run(self):
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
