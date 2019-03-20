import pygame
from pygame.math import Vector2 as Vect
import sys
import random
import math
import time


WHEELS_SPACING = 152
WHEEL_RADIUS = 30

white = (255,255,255)
black = (50,50,50)
blue = (0,0,255)
green = (0, 255, 0)
red = (255, 0, 0)
SENSORS_OFFSET = 0
CENTER_OF_ROTATION_OFFSET = 0
SENSORS_SPACING = 10
SENSORS_POS = [(2,-6),(0,0),(2,6)]#[(8,-6),(0,0),(8,6)]
PROXIMITY_SENSOR_OFFSET = 60
BREAKBEAM_SPACING = 38
BREAKBEAM_OFFSET = 58

class Car:
    def __init__(self, position, angle, background, tube_list):
        self.position = pygame.math.Vector2(position)
        self.angle = angle
        self.car_img = pygame.image.load('car.png').convert_alpha()
        self.background = background
        self.line_sensors_values = []
        self.speed_left = 0.0
        self.speed_right = 0.0
        self.tube_list = tube_list
        self.stocked_tube_list = []
        self.proximity_sensor_value = -1
        self.breakbeam_value = False
        for i in range(len(SENSORS_POS)):
            self.line_sensors_values.append(0)

    def draw(self, scr):
        """Draw the car on the surface scr
        """
        ###draw image
        rotated_image = pygame.transform.rotozoom(self.car_img, self.angle,1)
        rect = rotated_image.get_rect()
        rect.center = self.position + Vect(-CENTER_OF_ROTATION_OFFSET, 0).rotate(-self.angle)
        scr.blit(rotated_image, rect)

        ###draw center of rotation and wheels
        #pygame.draw.circle(scr, white, (int(self.position[0]), int(self.position[1])) , 2, 0)
        #wheel_L_pos = self.position + Vect(0, WHEELS_SPACING/2).rotate(-self.angle)
        #wheel_R_pos = self.position + Vect(0, -WHEELS_SPACING/2).rotate(-self.angle)
        #pygame.draw.circle(scr, red, (int(wheel_L_pos[0]), int(wheel_L_pos[1])), 1, 0)
        #pygame.draw.circle(scr, red, (int(wheel_R_pos[0]), int(wheel_R_pos[1])), 1, 0)

        ###draw line sensors
        sensors_center = rect.center  + Vect(-SENSORS_OFFSET, 0).rotate(-self.angle)
        for i in range(len(SENSORS_POS)):
            sensor_pos = sensors_center + Vect(SENSORS_POS[i][0], SENSORS_POS[i][1]).rotate(-self.angle)
            sensor_pos = (int(sensor_pos[0]), int(sensor_pos[1]))
            sensor_value = 0
            if 0 < sensor_pos[0] < 1350 and 0 < sensor_pos[1] < 725:
                if self.background.get_at(sensor_pos) == black:
                    sensor_value = 100
            self.line_sensors_values[i] = sensor_value
            if sensor_value > 50:
                color = red
            else:
                color = (192,133,133)
            pygame.draw.circle(scr, color, sensor_pos, 3, 0)

        ###proximity sensors
        # direction_vector = Vect(1,0).rotate(-self.angle)
        # current_pos = self.position + direction_vector*PROXIMITY_SENSOR_OFFSET
        # proximity_sensors_pos = (int(current_pos[0]), int(current_pos[1]))
        # distance = 0
        # found = False
        # while distance < 150 and not found:
        #     current_pos += direction_vector
        #     distance += 1
        #     if distance%14==0:
        #         pygame.draw.circle(scr, red, (int(current_pos[0]),int(current_pos[1])), 1, 0)
        #     for tube in self.tube_list:
        #         if tube.is_inside(current_pos):
        #             found = True
        #             break
        #
        # if found == True:
        #     color = (255-distance*150/150,0,0) #red
        #     self.proximity_sensor_value = distance
        # else:
        #     color = (192,133,133)
        #     self.proximity_sensor_value = -1
        # pygame.draw.circle(scr, color, proximity_sensors_pos, 2, 0)

        ###breakbeam sensors
        direction_vector = Vect(0,1).rotate(-self.angle)
        current_pos = self.position + Vect(BREAKBEAM_OFFSET,-BREAKBEAM_SPACING//2).rotate(-self.angle)
        breakbeam1_pos = (int(current_pos[0]), int(current_pos[1]))
        distance = 0
        found = False
        while distance < BREAKBEAM_SPACING:
            current_pos += direction_vector
            distance += 1
            for tube in self.tube_list:
                if tube.is_inside(current_pos):
                    found = True
        breakbeam2_pos = (int(current_pos[0]), int(current_pos[1]))
        if found == True:
            color = red
            self.breakbeam_value = True
        else:
            color = (192,133,133)
            self.breakbeam_value = False
        pygame.draw.circle(scr, color, breakbeam1_pos, 3, 0)
        pygame.draw.circle(scr, color, breakbeam2_pos, 3, 0)

    def update_pos(self, dt):
        """Compute the change in angle and position during the duration dt with current motor speeds
        """
        angular_speed = WHEEL_RADIUS*float(self.speed_left-self.speed_right)/WHEELS_SPACING
        linear_speed = WHEEL_RADIUS*float(self.speed_left+self.speed_right)/2
        self.angle -= math.degrees(angular_speed*dt)
        self.position[0] += linear_speed*math.cos(math.radians(self.angle))*dt
        self.position[1] -= linear_speed*math.sin(math.radians(self.angle))*dt
        self.angle = self.angle%360
        for tube in self.tube_list:
            if tube.is_inside(self.position) and tube.get_radius() != 10:
                self.stocked_tube_list.append(tube)
                self.tube_list.remove(tube)

    def set_speed(self, speed_left, speed_right):
        """Set the speed of both motors
        """
        self.speed_right = speed_right*2.6
        self.speed_left = speed_left*2.6


    def get_line_sensors_values(self):
        """Return a list of integers that contains the line sensor values from left to right
        """
        return self.line_sensors_values

    def get_proximity_sensor_value(self):
        return self.proximity_sensor_value

    def get_breakbeam_value(self):
        return self.breakbeam_value

    def get_speeds(self):
        return self.speed_left, self.speed_right

class Tube:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius

    def draw(self, scr):
        """Draw the tube on the surface scr
        """
        pygame.draw.circle(scr, (38,74,165), self.position, self.radius, 0)

    def set_pos(self, pos):
        """Set the center position of the tube
        """
        self.position = pos

    def is_inside(self, point):
        return Vect(point-self.position).length() < self.radius

    def get_radius(self):
        return self.radius

class Simulator:
    def __init__(self,(x,y,angle)):
        self.screen = pygame.display.set_mode((1350,725))
        pygame.init()
        pygame.display.set_caption('Simulation groupe 10')
        clock = pygame.time.Clock()
        pygame.font.init()
        self.myfont = pygame.font.SysFont('Times New Roman', 30)
        self.background, tube_point_list = self.get_background()
        tube_radius_list = [8,8,10,10,12,12]
        tube_point_list = random.sample(tube_point_list, len(tube_radius_list))
        self.tube_list = []

        for i in range(len(tube_radius_list)):
            self.tube_list.append(Tube(tube_point_list[i], tube_radius_list[i]))
        self.car = Car((x,y),angle, self.background, self.tube_list)

        self.speed_left_manual,self.speed_right_manual, self.speed_left_change, self.speed_right_change, self.angle_change, self.speed  = 0,0,0,0,0,0
        self.stop = True
        self.last_time = time.time()

    def get_background(self):
        """return the background surface and the list of all the possibles position of the tubes
        """
        background = pygame.Surface((1350,725))
        background.fill(white)
        pygame.draw.rect(background, black, (50,50,1250,625), 8)
        pygame.draw.line(background, black, (258,50), (258,675), 8)
        pygame.draw.line(background, black, (50,367), (258,367), 8)
        tube_point_list = []
        x = 327
        y = 147
        for i in range(6):
            pygame.draw.line(background, black, (x,y-4), (x,y+420), 9)
            tube_point_list.append((x,y+100))
            pygame.draw.line(background, black, (x-15,y+100), (x+15,y+100),9)
            tube_point_list.append((x,y+316))
            pygame.draw.line(background, black, (x-15,y+316), (x+15,y+316),9)
            if i%2==1 and i<5:
                pygame.draw.line(background, black, (x,y), (x+167,y),9)
            elif i<5:
                pygame.draw.line(background, black, (x,y+416), (x+167,y+416), 9)
            x+=167
        return background, tube_point_list

    def begin_loop(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                     pygame.quit();
                     sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.angle_change = 1
                    elif event.key == pygame.K_RIGHT:
                        self.angle_change = -1
                    elif event.key == pygame.K_UP:
                        self.speed = 2
                    elif event.key == pygame.K_DOWN:
                        self.speed = -2
                    elif event.key == pygame.K_u:
                        self.speed_left_change = 1
                    elif event.key == pygame.K_j:
                        self.speed_left_change = -1
                    elif event.key == pygame.K_o:
                        self.speed_right_change = 1
                    elif event.key == pygame.K_l:
                        self.speed_right_change = -1
                    elif event.key == pygame.K_SPACE:
                        self.stop = not self.stop
                    elif event.key == pygame.K_q:
                        pygame.quit();
                        sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT :
                        self.angle_change = 0
                    elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        self.speed = 0
                    elif event.key == pygame.K_u or event.key == pygame.K_j:
                        self.speed_left_change = 0
                    elif event.key == pygame.K_o or event.key == pygame.K_l:
                        self.speed_right_change = 0

    def end_loop(self, text):
        self.screen.blit(self.background, (0,0))
        for tube in self.tube_list:
            tube.draw(self.screen)
        self.car.update_pos(time.time()-self.last_time)
        self.last_time = time.time()
        self.car.draw(self.screen)
        text = self.myfont.render('x:'+str(

int(round(self.car.position[0]))) + ' y:'+str(

int(round(self.car.position[1])))  + ' angle:'+str(

int(round(self.car.angle)))\
         + ' Motors speeds: '+str(

int(round(self.car.speed_left)))+' | '+str(

int(round(self.car.speed_right)))+ ' ' +text , False, black)
        self.screen.blit(text,(0,0))
        pygame.display.update()

    def set_motor_speeds(self, speed_left,speed_right):
        #for keyboard control
        if self.stop:
            speed_left = 0
            speed_right = 0
        self.speed_left_manual += self.speed_left_change
        self.speed_right_manual += self.speed_right_change
        speed_left += self.speed - self.angle_change + self.speed_left_manual
        speed_right += self.speed + self.angle_change + self.speed_right_manual

        self.car.set_speed(speed_left, speed_right)

    def get_line_sensors_values(self):
        return self.car.get_line_sensors_values()

    def get_proximity_sensor_value(self):
        return self.car.get_proximity_sensor_value()

    def get_breakbeam_value(self):
        return self.car.get_breakbeam_value()

    def get_true_speeds(self):
        return self.car.get_speeds()
