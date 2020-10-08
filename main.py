import math
import os
import random
import pygame

from math import sin, radians, degrees, cos
from pygame.math import *

width = 1024
height = 768
SIZE = [width, height]
MAX_BEAM_LEN = 100

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
Yellow = (255, 255, 0)

surface = pygame.display.set_mode((width, height))

mask_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
mask_surface.fill((255, 0, 0))

mask = pygame.mask.from_surface(mask_surface)
mask_fx = pygame.mask.from_surface(pygame.transform.flip(mask_surface, True, False))
mask_fy = pygame.mask.from_surface(pygame.transform.flip(mask_surface, False, True))
mask_fx_fy = pygame.mask.from_surface(pygame.transform.flip(mask_surface, True, True))
flipped_masks = [[mask, mask_fy], [mask_fx, mask_fx_fy]]

PPU = 64
class Car:

    def __init__(self, x, y, angle=0.0, length=3, max_steering=30, max_acceleration=3.0):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "mini_car.png")

        self.car_image = pygame.image.load(image_path)
        self.carinit_position = Vector2(0, 0)
        self.flag = True

        self.position = Vector2(x, y)
        self.real_position = Vector2(x,y)
        self.center_position = Vector2(x,y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 20
        self.brake_deceleration = 10
        self.free_deceleration = 2
        self.acceleration = 0.0
        self.steering = 0.0

    def update(self, dt):
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity,
                              min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt

        # Make car rect
        self.rotated = pygame.transform.rotate(self.car_image, self.angle)
        rotated_rect = self.rotated.get_rect()

        # Calculate position
        self.real_position = self.position * PPU

        self.center_position.x = self.real_position.x + rotated_rect.width / 2
        self.center_position.y = self.real_position.y + rotated_rect.height / 2

    # def update(self, dt):
    #     self.velocity += (self.acceleration * dt, 0)
    #     self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))
    #
    #     if self.steering:
    #         turning_radius = self.length / sin(radians(self.steering))
    #         angular_velocity = self.velocity.x / turning_radius
    #     else:
    #         angular_velocity = 0
    #
    #     if width / 64 >= self.position.x >= 0 and height / 64 >= self.position.y >= 0:
    #         self.position += self.velocity.rotate(-self.angle) * dt
    #         # self.angle += degrees(angular_velocity) * dt
    #     else:
    #         self.position.x = self.carinit_position.x
    #         self.position.y = self.carinit_position.y
    #         self.velocity = Vector2(0.0, 0.0)
    #         self.angle = random.uniform(0, 180)
    #         # print("new generation ")

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Car tutorial")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.back_img_path = os.path.join(current_dir, "background.png")
        self.map_surface = pygame.image.load(self.back_img_path)
        self.map_mask = pygame.mask.from_surface(self.map_surface)

        self.beam_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.beam_mask = pygame.mask.from_surface(self.beam_surface)

        self.game_start = False
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False

    def run(self):
        car = Car(0, 0)

        while not self.exit:
            dt = self.clock.get_time() / 1000
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game_start = True

            # Drawing
            self.screen.fill((0, 0, 0, 0))
            self.screen.blit(self.map_surface, (0, 0))
            self.printText("car position: " + str(car.position), 3, 3)
            self.printText("car steering: " + str(car.steering), 3, 20)
            self.printText("car velocity: " + str(car.velocity[0]), 3, 37)
            self.printText("car acceleration: " + str(car.acceleration), 3, 54)
            self.printText("car angle : " + str(car.angle), 3, 71)

            # Logic
            # Start Car position
            if car.flag:
                print("start car")
                car.flag = False
                car.carinit_position.x = 0 / PPU
                car.carinit_position.y = 322 / PPU
                car.position.x = 0 / PPU
                car.position.y = 322 / PPU

            if self.game_start:
                car.steering = random.uniform(0, car.max_steering) * dt
                car.acceleration = random.uniform(0, car.max_acceleration)
                car.update(dt)

            rotated = pygame.transform.rotate(car.car_image, car.angle)
            rect = rotated.get_rect()
            carNewPos = Vector2(car.position.x * PPU + rect.width / 2, car.position.y * PPU + rect.height / 2)

            pygame.draw.line(self.screen,BLACK,car.carinit_position,car.position)
            self.draw_beam(car.angle - 15, carNewPos)
            self.draw_beam(car.angle, carNewPos)
            self.draw_beam(car.angle + 15, carNewPos)
            self.screen.blit(rotated, carNewPos)
            pygame.display.flip()
            self.clock.tick(self.ticks)

        pygame.quit()

    def printText(self, text, x, y):
        # 현재 디렉토리로부터 myfont.ttf 폰트 파일을 로딩한다. 텍스트 크기를 32로 한다
        fontObj = pygame.font.Font('HoonWhitecatR.ttf', 15)
        printText = text

        # 텍스트 객체를 생성한다. 첫번째 파라미터는 텍스트 내용, 두번째는 Anti-aliasing 사용 여부, 세번째는 텍스트 컬러를 나타낸다
        printTextObj = fontObj.render(printText, True, WHITE)

        # 텍스트 객체의 출력 위치를 가져온다
        printTextRect = printTextObj.get_rect()

        # 텍스트 객체의 출력 중심 좌표를 설정한다
        printTextRect.topleft = (x, y)
        self.screen.blit(printTextObj, printTextRect)

    def draw_beam(self, angle, pos):

        x_dest = pos[0] + MAX_BEAM_LEN * math.cos(-math.radians(angle))
        y_dest = pos[1] + MAX_BEAM_LEN * math.sin(-math.radians(angle))

        self.beam_surface.fill((0, 0, 0, 0))
        # draw a single beam to the beam surface based on computed final point
        pygame.draw.line(self.beam_surface, BLUE, pos, (x_dest, y_dest))
        beam_mask = pygame.mask.from_surface(self.beam_surface)
        hit = self.map_mask.overlap(beam_mask, (0, 0))
        # pygame.draw.circle(self.screen, RED, pos, 5)
        if hit is not None:
            # hx = self.width - start_position.x if flip_x else start_position.x
            # hy = self.height - start_position.y if flip_y else start_position.y
            # hit_pos = (hx, hy)

            pygame.draw.line(self.screen, WHITE, pos, hit)
            pygame.draw.circle(self.screen, RED, hit, 3)

        else:
            pygame.draw.line(self.screen, WHITE, pos, (x_dest, y_dest))


if __name__ == '__main__':
    game = Game()
    game.run()
