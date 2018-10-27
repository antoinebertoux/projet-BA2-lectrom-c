import pygame
import sys
import random
import math

white = (255,255,255)
black = (0,0,0)
blue = (0,0,255)
green = (0, 255, 0)
red = (255, 0, 0)

class Tube:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius
    def draw(self, scr):
        pygame.draw.circle(scr, blue, self.position, self.radius, 0)
    def set_pos(self, pos):
        self.position = pos

class Car:
    def __init__(self, background):
        self.position = pygame.math.Vector2(0,0)
        self.angle = 0
        self.car_img = pygame.image.load('car.png').convert_alpha()
        #vector from center of image to center of rotation
        self.offset = pygame.math.Vector2(-60, 0)
        #vector from center of rotation to sensor
        self.sensor_offset = pygame.math.Vector2(-30, 0)
        self.background = background
        self.sensors_values = [False, False, False]
    def draw(self, scr):
        ###draw image
        offset_rotated = self.offset.rotate(-self.angle)
        rotated_image = pygame.transform.rotate(self.car_img, self.angle)
        rect = rotated_image.get_rect()
        rect.center = self.position + offset_rotated
        scr.blit(rotated_image, rect)

        ###draw center of rotation
        pygame.draw.circle(scr, white, self.position, 2, 0)

        ###draw sensors
        sensor_offset_rotated = self.offset.rotate(-self.angle)
        sensor_offset_rotated_perpendicular = sensor_offset_rotated.rotate(90)
        sensors_center = self.position + sensor_offset_rotated
        n = len(self.sensors_values)
        for i in range(n):
            sensor_pos = sensors_center + (i-n//2)*sensor_offset_rotated_perpendicular*0.3
            sensor_pos = (int(sensor_pos[0]), int(sensor_pos[1]))
            sensor_value = (background.get_at(sensor_pos) == black)
            self.sensors_values[i] = sensor_value
            if sensor_value:
                color = red
            else:
                color = green
            pygame.draw.circle(scr, color, sensor_pos, 5, 0)
    def set_pos(self, pos):
        self.position = pos
    def set_angle(self, ang):
        self.angle = angle
    def get_sensors_values(self):
        return self.sensors_values

def get_background():
    background = pygame.Surface((1500,800))
    background.fill(white)
    pygame.draw.rect(background, black, (50,50,1400,700), 16)
    pygame.draw.line(background, black, (285,50), (285,750), 16)
    pygame.draw.line(background, black, (50,400), (285,400), 16)
    tube_point_list = []
    x = 360
    y = 160
    for i in range(6):
        pygame.draw.line(background, black, (x,y), (x,y+470), 16)
        tube_point_list.append((x,y+110))
        tube_point_list.append((x,y+360))
        if i%2==1 and i<5:
            pygame.draw.line(background, black, (x,y), (x+200,y), 16)
        elif i<5:
            pygame.draw.line(background, black, (x,y+470), (x+200,y+470), 16)
        x+=200
    return background, tube_point_list

screen = pygame.display.set_mode((1500,800))
pygame.init()
pygame.display.set_caption('Simulation groupe 10')
clock = pygame.time.Clock()

background, tube_point_list = get_background()
tube_point_list = random.sample(tube_point_list, 6)
tube_radius_list = [16,16,20,20,25,25]
tube_list = []
for i in range(6):
    tube_list.append(Tube(tube_point_list[i], tube_radius_list[i]))

x =  (360)
y = (160)
x_change = 0
y_change = 0
car_speed = 0
angle_change = 0
angle = 270
car = Car(background)
while True:
    ###update position
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 pygame.quit();
                 sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -1
                elif event.key == pygame.K_RIGHT:
                    x_change = 1
                elif event.key == pygame.K_UP:
                    y_change = -1
                elif event.key == pygame.K_DOWN:
                    y_change = 1
                elif event.key == pygame.K_a:
                    angle_change = 1
                elif event.key == pygame.K_z:
                    angle_change = -1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT :
                    x_change = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    y_change = 0
                elif event.key == pygame.K_a or event.key == pygame.K_z:
                    angle_change = 0
    x += x_change
    y += y_change
    angle += angle_change
    angle = angle%360

    car.set_pos((x,y))
    car.set_angle(angle)

    ###draw everything
    screen.blit(background, (0,0))
    for tube in tube_list:
        tube.draw(screen)
    car.draw(screen)
    pygame.display.update()
