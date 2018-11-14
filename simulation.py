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
WHEELS_SPACING = 145
SENSORS_OFFSET = -0
CENTER_OF_ROTATION_OFFSET = -5
SENSORS_SPACING = 10
SENSORS_POS = [(0,-9),(5,0),(0,9)]
PROXIMITY_SENSOR_OFFSET = 60

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
        for i in range(len(SENSORS_POS)):
            self.line_sensors_values.append(0)

    def draw(self, scr):
        """Draw the car on the surface scr
        """
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
                color = green
            pygame.draw.circle(scr, color, sensor_pos, 3, 0)

        ###proximity sensors
        direction_vector = Vect(1,0).rotate(-self.angle)
        current_pos = self.position + direction_vector*PROXIMITY_SENSOR_OFFSET
        proximity_sensors_pos = (int(current_pos[0]), int(current_pos[1]))
        distance = 0
        found = False
        while distance < 150 and not found:
            current_pos += direction_vector
            distance += 1
            for tube in self.tube_list:
                if tube.is_inside(current_pos):
                    found = True
                    print(distance)
                    break

        if found == True:
            color = (255-distance*150/150,0,0) #red
            self.proximity_sensor_value = distance
        else:
            color = green
            self.proximity_sensor_value = -1
        pygame.draw.circle(scr, color, proximity_sensors_pos, 5, 0)


    def update_pos(self, dt):
        """Compute the change in angle and position during the duration dt with current motor speeds
        """
        angular_speed = float(self.speed_left-self.speed_right)/WHEELS_SPACING
        linear_speed = float(self.speed_left+self.speed_right)/2
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
        DIFF = 100 #depends on acceleration/inertia
        if speed_left+DIFF < self.speed_left:
            self.speed_left -= DIFF
        elif speed_left-DIFF > self.speed_left:
            self.speed_left += DIFF
        else:
            self.speed_left = speed_left

        if speed_right+DIFF < self.speed_right:
            self.speed_right -= DIFF
        elif speed_right-DIFF > self.speed_right:
            self.speed_right += DIFF
        else:
            self.speed_right = speed_right

    def get_line_sensors_values(self):
        """Return a list of integers that contains the line sensor values from left to right
        """
        return self.line_sensors_values
    def get_proximity_sensor_value(self):
        return self.proximity_sensor_value
class Tube:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius

    def draw(self, scr):
        """Draw the tube on the surface scr
        """
        pygame.draw.circle(scr, blue, self.position, self.radius, 0)

    def set_pos(self, pos):
        """Set the center position of the tube
        """
        self.position = pos

    def is_inside(self, point):
        return Vect(point-self.position).length() < self.radius

    def get_radius(self):
        return self.radius

def get_background():
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
        tube_point_list.append((x,y+316))
        if i%2==1 and i<5:
            pygame.draw.line(background, black, (x,y), (x+167,y),9)
        elif i<5:
            pygame.draw.line(background, black, (x,y+416), (x+167,y+416), 9)
        x+=167
    return background, tube_point_list


######  Main code ######
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

car = Car((328,150), 270, background, tube_list)

pv = 0
SP = 10
error = 0
turning = ""
number_of_turns = 0

#retour
retour = False
retour0 = False
tretour = 0

speed_left, speed_right, speed_left_manual,speed_right_manual, speed_left_change, speed_right_change, angle_change, speed  = 0,0,0,0,0,0,0,0
stop = True
last_time = time.time()
distance_since_last_turn = 0
slowing_down = False
slowing_down_start = 0

##### Main loop ######
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

    sensor_values = car.get_line_sensors_values()
    total_sum = sensor_values[0] + sensor_values[1] + sensor_values[2]
    if total_sum == 0:
        pv = 10
    else:
        pv = (sensor_values[0] + sensor_values[1]*10 + sensor_values[2]*20)/total_sum
    error = pv-SP

    proximity_sensor_value = car.get_proximity_sensor_value()
    if 0 < proximity_sensor_value < 20 and not slowing_down:
        #start slowing down
        slowing_down_start = time.time()
        slowing_down = True

    if time.time()-slowing_down_start > 2:
        #stop slowing down
        slowing_down = False

    if slowing_down:
        default_speed = 30
    else:
        default_speed = 65

    if turning == "left" or turning == "right":
        #turning
        if time.time() - turning_start < 0.2:
            speed_left = 50
            speed_right = 50
        elif time.time() - turning_start < 2.35:
            if turning == "left":
                speed_left = -50
                speed_right = 50
            else:
                speed_left = 50
                speed_right = -50
        else:
            #stop turning
            turning = ""
            distance_since_last_turn = 0
            number_of_turns+=1
    else:
        #following line
        if error == 0 and total_sum<200:
            #keep following line
            speed_left = default_speed
            speed_right = default_speed
        else:
            if ((distance_since_last_turn>390 and number_of_turns % 2==0) or (distance_since_last_turn>150 and number_of_turns % 2==1))\
            and number_of_turns < 10:
                #start turning
                turning_start = time.time()
                if error > 0:
                    turning = "right"
                    speed_left = 50
                    speed_right = -50
                else:
                    turning = "left"
                    speed_left = -50
                    speed_right = 50
            else:
                #keep following line
                speed_left = default_speed + error*7
                speed_right = default_speed - error*7

    #retour
    dtretour = 0
    if not total_sum and not retour0 and not retour : # on est sortie de la route
        tretour = time.time()
        t0 = time.time()
        retour0 = True
        #print(1)
    elif retour0 and total_sum >= 10 :# finalement on est a nouveau sur la route
        tretour = 0
        retour0 = False
        #print(2)
    elif retour0 and (last_time-tretour> 0.5) : # on est sortie de la route depuis trop longtemps pour que ce soit une erreur donc on desside de rentre
        t0 = time.time()
        retour = True
        retour0 = False
    elif retour : # on a decide de rentre
        t1 = time.time()
        dtretour = t1-t0
        #print(4)
        if dtretour <= 2.25 : # on tourne a gauche
            speed_left = -50
            speed_right = 50
        elif dtretour <= 12 and dtretour > 2.25 : # on va tout droit
            speed_left = 100
            speed_right = 100
        elif dtretour <= 14.25 and dtretour > 12 : # on tourne a gauche
            speed_right = 50
            speed_left = -50
        elif dtretour <= 16.25 and dtretour > 14.25 : # on s'arrete pour deposser des cylindres
            speed_right = 0
            speed_left = 0
        elif dtretour <= 21 and dtretour > 16.25 : # on va tout droit
            speed_left = 100
            speed_right = 100
        elif dtretour > 21 : # on fini de deposse les derniers cylindres
            speed_right = 0
            speed_left = 0

    #for keyboard control
    if stop:
        speed_left = 0
        speed_right = 0
    speed_left_manual += speed_left_change
    speed_right_manual += speed_right_change
    speed_left += speed - angle_change + speed_left_manual
    speed_right += speed + angle_change + speed_right_manual


    distance_since_last_turn += float(speed_left+speed_right)/2*dt

    car.set_speed(speed_left, speed_right)

    ###draw everything
    screen.blit(background, (0,0))
    for tube in tube_list:
        tube.draw(screen)
    car.update_pos(dt)
    car.draw(screen)
    text = myfont.render('x:'+str(round(car.position[0])) + ' y:'+str(round(car.position[1]))  + ' angle:'+str(round(car.angle))\
     + ' Motors speeds: '+str(round(speed_left))+' | '+str(round(speed_right))+'  Error: '+str(error) + ' Timer: ' +str(round(dtretour*10)/10) , False, black)
    screen.blit(text,(0,0))
    pygame.display.update()

    time.sleep(0.05)
