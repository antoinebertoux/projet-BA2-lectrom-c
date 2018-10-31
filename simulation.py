import pygame
from pygame.math import Vector2 as Vect
import sys
import random
import math
import time

white = (255,255,255)
black = (0,0,0)
blue = (0,0,255)
green = (0, 255, 0)
red = (255, 0, 0)

WHEELS_SPACING = 140
SENSORS_OFFSET = -5
CENTER_OF_ROTATION_OFFSET = -5
SENSORS_SPACING = 6
NUMBER_OF_SENSOR = 3

class Car:
    def __init__(self, position, angle, background):
        self.position = pygame.math.Vector2(position)
        self.angle = angle
        self.car_img = pygame.image.load('car.png').convert_alpha()
        self.background = background
        self.sensors_values = []
        self.speed_left = 0.0
        self.speed_right = 0.0
        for i in range(NUMBER_OF_SENSOR):
            self.sensors_values.append(0)

    def draw(self, scr):
        ###draw image
        rotated_image = pygame.transform.rotate(self.car_img, self.angle)
        rect = rotated_image.get_rect()
        rect.center = self.position + Vect(-CENTER_OF_ROTATION_OFFSET, 0).rotate(-self.angle)
        scr.blit(rotated_image, rect)

        ###draw center of rotation and wheels
        pygame.draw.circle(scr, white, (int(self.position[0]), int(self.position[1])) , 2, 0)
        wheel_L_pos = self.position + Vect(0, WHEELS_SPACING/2).rotate(-self.angle)
        wheel_R_pos = self.position + Vect(0, -WHEELS_SPACING/2).rotate(-self.angle)
        pygame.draw.circle(scr, black, (int(wheel_L_pos[0]), int(wheel_L_pos[1])), 5, 0)
        pygame.draw.circle(scr, black, (int(wheel_R_pos[0]), int(wheel_R_pos[1])), 5, 0)

        ###draw sensors
        sensors_center = rect.center  + Vect(-SENSORS_OFFSET, 0).rotate(-self.angle)
        for i in range(NUMBER_OF_SENSOR):
            sensor_pos = sensors_center + (i-NUMBER_OF_SENSOR//2)*Vect(0, -SENSORS_SPACING).rotate(-self.angle)
            sensor_pos = (int(sensor_pos[0]), int(sensor_pos[1]))
            sensor_value = 0
            if 0 < sensor_pos[0] < 1350 and 0 < sensor_pos[1] < 725:
                if self.background.get_at(sensor_pos) == black:
                    sensor_value = 100
            self.sensors_values[i] = sensor_value
            if sensor_value > 50:
                color = red
            else:
                color = green
            pygame.draw.circle(scr, color, sensor_pos, 3, 0)

    def update_pos(self, dt):
        angular_speed = float(self.speed_left-self.speed_right)/WHEELS_SPACING
        linear_speed = float(self.speed_left+self.speed_right)/2
        self.angle -= math.degrees(angular_speed*dt)
        self.position[0] += linear_speed*math.cos(math.radians(self.angle))*dt
        self.position[1] -= linear_speed*math.sin(math.radians(self.angle))*dt
        self.angle = self.angle%360

    def set_speed(self, speed_left, speed_right):
        self.speed_left = speed_left
        self.speed_right = speed_right

    def get_sensors_values(self):
        return self.sensors_values

class Tube:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius
    def draw(self, scr):
        pygame.draw.circle(scr, blue, self.position, self.radius, 0)
    def set_pos(self, pos):
        self.position = pos

def get_background():
    background = pygame.Surface((1350,725))
    background.fill(white)
    pygame.draw.rect(background, black, (50,50,1250,625), 8)
    pygame.draw.line(background, black, (258,50), (258,675), 8)
    pygame.draw.line(background, black, (50,367), (258,367), 8)
    tube_point_list = []
    x = 327
    y = 147
    for i in range(6):
        pygame.draw.line(background, black, (x,y), (x,y+416), 8)
        tube_point_list.append((x,y+100))
        tube_point_list.append((x,y+316))
        if i%2==1 and i<5:
            pygame.draw.line(background, black, (x,y), (x+167,y), 8)
        elif i<5:
            pygame.draw.line(background, black, (x,y+416), (x+167,y+416), 8)
        x+=167
    return background, tube_point_list


#Main code
screen = pygame.display.set_mode((1350,725))
pygame.init()
pygame.display.set_caption('Simulation groupe 10')
clock = pygame.time.Clock()
pygame.font.init()
myfont = pygame.font.SysFont('Times New Roman', 30)

background, tube_point_list = get_background()
tube_radius_list = [8,8,10,10,12,12]
tube_point_list = random.sample(tube_point_list, len(tube_radius_list))
tube_list = []
for i in range(len(tube_radius_list)):
    tube_list.append(Tube(tube_point_list[i], tube_radius_list[i]))

car = Car((327,300), 269, background)

#PID
pv = 0
MAX = (NUMBER_OF_SENSOR-1) * 10
SP = MAX/2
error = 0
last_error = 0
integral = 0
KP = 35
KI = 0
KD = 0
correction = 0

speed_left, speed_right, speed_left_manual,speed_right_manual, speed_left_change, speed_right_change, angle_change, speed  = 0,0,0,0,0,0,0,0
stop = True
last_time = time.time()

while True:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 pygame.quit();
                 sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    angle_change = 100
                elif event.key == pygame.K_RIGHT:
                    angle_change = -100
                elif event.key == pygame.K_UP:
                    speed = 110
                elif event.key == pygame.K_DOWN:
                    speed = -110
                elif event.key == pygame.K_u:
                    speed_left_change = 3
                elif event.key == pygame.K_j:
                    speed_left_change = -3
                elif event.key == pygame.K_o:
                    speed_right_change = 3
                elif event.key == pygame.K_l:
                    speed_right_change = -3
                elif event.key == pygame.K_SPACE:
                    stop = not stop
                elif event.key == pygame.K_q:
                    pygame.quit();
                    sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT :
                    angle_change = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    speed = 0
                elif event.key == pygame.K_u or event.key == pygame.K_j:
                    speed_left_change = 0
                elif event.key == pygame.K_o or event.key == pygame.K_l:
                    speed_right_change = 0

    dt = time.time()-last_time
    last_time = time.time()

    #PID
    sensor_values = car.get_sensors_values()
    weighted_sum = 0
    total_sum = 0
    weight = 0
    for value in sensor_values:
        total_sum += value
        weighted_sum += weight * value
        weight += 10
    if total_sum == 0:
        if pv >MAX/2:
            pv = MAX
        else:
            pv = 0
    else:
        pv = weighted_sum/total_sum
    error = pv-SP
    integral += last_error*dt
    correction = KP * error + KD * (error - last_error)/dt + KI * integral
    last_error = error
    speed_left = 50 - correction
    speed_right = 50 + correction

    #for keyboard control
    if stop:
        speed_left = 0
        speed_right = 0
    speed_left_manual += speed_left_change
    speed_right_manual += speed_right_change
    speed_left += speed - angle_change + speed_left_manual
    speed_right += speed + angle_change + speed_right_manual

    car.set_speed(speed_left, speed_right)

    ###draw everything
    screen.blit(background, (0,0))
    for tube in tube_list:
        tube.draw(screen)
    car.update_pos(dt)
    car.draw(screen)
    text = myfont.render('Motors speeds: '+str(round(speed_left))+' | '+str(round(speed_right))+'  Error: '+str(error), False, black)
    screen.blit(text,(0,0))
    pygame.display.update()

    time.sleep(0.05)
