from simulator import Simulator
import time
import math

start_pos_begining = 328,150,270
start_pos_end = 1164,272, 90
simulator = Simulator(start_pos_begining)

#######
#SETUP#
#######

WHEELS_SPACING = 152
WHEEL_RADIUS = 30
SLOW_SPEED = 0.4
NORMAL_SPEED = 1
TURNING_SPEED = 0.8
START_TURN_DELAY = 5

error = 0
turning = ""
number_of_turns = 0

retour = False
retour0 = False
tretour = 0

distance_since_last_turn = 0
slowing_down = False
slowing_down_start = 0
slowing_down_distance = 0
angle_turned = 90
distance_step = 0
start_turn_delay_count = 0
angle_step = 0
Kp =0.05
last_time = time.time()
current_time = time.time()
breakbeam_value = False
diameter = 0
last_diameter = 0

######
#LOOP#
######
while True:
    simulator.begin_loop()

    current_time = time.time()
    dt = current_time-last_time
    last_time = time.time()

    sensor_values = simulator.get_line_sensors_values()
    total_sum = sensor_values[0] + sensor_values[1] + sensor_values[2]
    if total_sum == 0:
        error = 0
    else:
        error = (sensor_values[0] + sensor_values[1]*10 + sensor_values[2]*20)/total_sum - 10

    proximity_sensor_value = simulator.get_proximity_sensor_value()
    if 0 < proximity_sensor_value < 30 and not slowing_down:
        #start slowing down
        slowing_down_distance = 0
        slowing_down = True

    if slowing_down and slowing_down_distance > 70:
        #stop slowing down
        slowing_down = False
        last_diameter = diameter
        DIAMETER_TOLERANCES = [13, 18, 22, 27]
        if DIAMETER_TOLERANCES[0] < diameter <= DIAMETER_TOLERANCES[1]:
            print("petit")
        elif DIAMETER_TOLERANCES[1] < diameter <= DIAMETER_TOLERANCES[2]:
            print("moyen")
        elif DIAMETER_TOLERANCES[2] < diameter <= DIAMETER_TOLERANCES[3]:
            print("grand")
        diameter = 0

    if slowing_down:
        default_speed = SLOW_SPEED
        slowing_down_distance += distance_step
    else:
        default_speed = NORMAL_SPEED

    breakbeam_value = simulator.get_breakbeam_value()
    if breakbeam_value:
        diameter += distance_step

    if turning == "left" or turning == "right":
        #turning
        if 0 <= start_turn_delay_count < START_TURN_DELAY:
            start_turn_delay_count += distance_step
        elif abs(angle_turned)<=90 and start_turn_delay_count > START_TURN_DELAY:
            if turning == "left":
                speed_left = -TURNING_SPEED
                speed_right = TURNING_SPEED
            else:
                speed_left = TURNING_SPEED
                speed_right = -TURNING_SPEED
        else:
            #stop turning
            turning = ""
            distance_since_last_turn = 0
            number_of_turns+=1
            speed_left = NORMAL_SPEED
            speed_right = NORMAL_SPEED
    else:
        #following line
        if error == 0 and total_sum<200:
            #keep following line
            speed_left = default_speed
            speed_right = default_speed
        else:
            if ((distance_since_last_turn>400 and number_of_turns % 2==0) or (distance_since_last_turn>150 and number_of_turns % 2==1))\
            and number_of_turns < 10 and ((number_of_turns//2)%2 == 1) == (error>0):

                #start turning
                angle_turned = 0
                start_turn_delay_count = 0
                speed_left = default_speed
                speed_right = default_speed
                if (number_of_turns//2)%2 == 1:
                    turning = "right"
                else:
                    turning = "left"
            else:
                #keep following line
                speed_left = default_speed + error*Kp
                speed_right = default_speed - error*Kp

    #retour
    dtretour = 0
    if not total_sum and not retour0 and not retour : # on est sortie de la route
        tretour = time.time()
        t0 = time.time()
        retour0 = True
    elif retour0 and total_sum >= 10 :# finalement on est a nouveau sur la route
        tretour = 0
        retour0 = False
    elif retour0 and (last_time-tretour> 0.5) : # on est sortie de la route depuis trop longtemps pour que ce soit une erreur donc on desside de rentre
        t0 = time.time()
        retour0 = False

        retour = True
        step_number = 1
        angle_turned = 0
    elif retour : # on a decide de rentre
        if step_number == 1:
            if angle_turned < 86:
                speed_left = -TURNING_SPEED
                speed_right = TURNING_SPEED
            else:
                step_number = 2
                distance_since_last_turn = 0
        if step_number == 2:
            if distance_since_last_turn < 1000:
                speed_left = NORMAL_SPEED
                speed_right = NORMAL_SPEED
            else:
                step_number = 3
                angle_turned = 0
        if step_number == 3:
            if angle_turned < 86:
                speed_left = -TURNING_SPEED
                speed_right = TURNING_SPEED
            else:
                step_number = 4
                start_time = time.time()
        if step_number == 4:
            if current_time - start_time < 2:
                speed_left = 0
                speed_right = 0
            else:
                step_number = 5
                distance_since_last_turn = 0
        if step_number == 5:
            if distance_since_last_turn < 400:
                speed_left = NORMAL_SPEED
                speed_right = NORMAL_SPEED
            else:
                step_number = 6
        if step_number == 6:
            speed_left = 0
            speed_right = 0

    true_speed_right, true_speed_left = simulator.get_true_speeds()
    distance_step = WHEEL_RADIUS*float(true_speed_left+true_speed_right)/2*dt
    angle_step = math.degrees(WHEEL_RADIUS*float(true_speed_left-true_speed_right)/WHEELS_SPACING*dt)

    distance_since_last_turn += distance_step
    angle_turned += angle_step

    simulator.set_motor_speeds(speed_left, speed_right)

    text_to_display = 'Error: '+str(error) + ' Angle_turned: ' +str(

int(round(angle_turned))) + ' distance: ' + str(

int(round(distance_since_last_turn)))+ ' diameter: ' + str(round(last_diameter,2))

    simulator.end_loop(text_to_display)
    time.sleep(0.05)
