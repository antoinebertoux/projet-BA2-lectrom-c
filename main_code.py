from simulator import Simulator
import time
import math

######
#INIT#
######

simulator = Simulator()
pv = 0
SP = 10
error = 0
turning = ""
number_of_turns = 0
WHEELS_SPACING = 152

retour = False
retour0 = False
tretour = 0

distance_since_last_turn = 0
slowing_down = False
slowing_down_start = 0
angle_turned = 90
Kp =5
last_time = time.time()

######
#LOOP#
######
while True:
    simulator.begin_loop()

    dt = time.time()-last_time
    last_time = time.time()

    sensor_values = simulator.get_line_sensors_values()
    total_sum = sensor_values[0] + sensor_values[1] + sensor_values[2]
    if total_sum == 0:
        pv = 10
    else:
        pv = (sensor_values[0] + sensor_values[1]*10 + sensor_values[2]*20)/total_sum
    error = pv-SP

    proximity_sensor_value = simulator.get_proximity_sensor_value()
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
        if time.time() - turning_start < 0.3:
            speed_left = 50
            speed_right = 50
        elif abs(angle_turned)<=90:
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
            speed_left = 50
            speed_right = 50
    else:
        #following line
        if error == 0 and total_sum<200:
            #keep following line
            speed_left = default_speed
            speed_right = default_speed
        else:
            if ((distance_since_last_turn>400 and number_of_turns % 2==0) or (distance_since_last_turn>150 and number_of_turns % 2==1))\
            and number_of_turns < 10:
                #start turning
                turning_start = time.time()
                angle_turned = 0
                if (number_of_turns//2)%2 == 1:
                    turning = "right"
                    speed_left = 50
                    speed_right = -50
                else:
                    turning = "left"
                    speed_left = -50
                    speed_right = 50
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

    distance_since_last_turn += float(speed_left+speed_right)/2*dt
    angle_turned += math.degrees(float(speed_left-speed_right)/WHEELS_SPACING*dt)

    simulator.set_motor_speeds(speed_left, speed_right)

    text_to_display = 'Error: '+str(error) + ' Timer: ' +str(round(dtretour*10)/10)

    simulator.end_loop(text_to_display)
    time.sleep(0.05)
