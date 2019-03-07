from simulator import Simulator
import time
import math
import copy

start_pos_begining = 328,150,270
start_pos_end = 1164,272, 90
simulator = Simulator(start_pos_begining)

#######
#SETUP#
#######

WHEELS_SPACING = 152
WHEEL_RADIUS = 30
NORMAL_SPEED = 0.65
TURNING_SPEED = 0.8
DIAMETER_TOLERANCES = [13, 18, 22, 27]
TURN_AFTER_DISTANCE_1 = 390
TURN_AFTER_DISTANCE_2 = 140

error = 0
state = "following_line"
mark_number = 0

angle_turned = 90
total_distance = 0
K =0.05
last_time = time.time()
current_time = time.time()
breakbeam_value = False
diameter = 0
last_breakbeam_value = False
last_action_distance = 0
start_turning_angle = 0
action_number = 0
last_mark_distance = -1000
action_list = []
TURN_LEFT = [["turning_left", 90]]
TURN_RIGHT = [["turning_right", 90]]
STOCK_TUBE = [["stop",1.3]]
MIDDLE_DIAM = [["following_line", 38], ["stop",2],["following_line", 20],["stop",1.3]]

RETURN = [["turning_left", 180],["following_line", 100],["turning_right", 90], ["going_straight", 1000], ["stop", 1000]]
last_action_time = 0
tube_enter_distance = 0
def next_action():
    global action_number, start_turning_angle, last_action_distance, last_action_time
    action_number +=1
    start_turning_angle = angle_turned
    last_action_distance = total_distance
    last_action_time = time.time()
def set_maneuver(list):
    global action_list, action_number
    action_list = copy.deepcopy(list)
    next_action()
    action_number = 0
def add_maneuver(list):
    global action_list
    if len(action_list)==0:
        set_maneuver(list)
    else:
        action_list+=list
######
#LOOP#
######
while True:
    simulator.begin_loop()

    current_time = time.time()
    dt = current_time-last_time
    last_time = time.time()

    speed_left = NORMAL_SPEED
    speed_right = NORMAL_SPEED

    sensor_values = simulator.get_line_sensors_values()
    total_sum = sensor_values[0] + sensor_values[1] + sensor_values[2]
    if total_sum == 0:
        error = 0
    else:
        error = (sensor_values[0] + sensor_values[1]*10 + sensor_values[2]*20)/total_sum - 10

    breakbeam_value = simulator.get_breakbeam_value()

    if breakbeam_value and not last_breakbeam_value:
        tube_enter_distance = total_distance

    if not breakbeam_value and last_breakbeam_value:
        #stop slowing down
        diameter = total_distance - tube_enter_distance
    last_breakbeam_value = breakbeam_value

    if action_number<len(action_list):
        state = action_list[action_number][0]
        target_val = action_list[action_number][1]
    else:
        state = "following_line"
        target_val = 0

    if state == "following_line":
        #following line
        if total_distance-last_action_distance <= target_val or target_val == 0:
            if total_distance-last_mark_distance < 30:
                speed_left = NORMAL_SPEED
                speed_right = NORMAL_SPEED
            elif sensor_values[0] and sensor_values[2]:
                if mark_number !=0:
                    if mark_number >= 11:
                        set_maneuver(RETURN)
                    elif (mark_number-1)//2%2==0:
                        set_maneuver(TURN_LEFT)
                    elif (mark_number-1)//2%2==1:
                        set_maneuver(TURN_RIGHT)
                mark_number+=1
                print(mark_number)
                if diameter == 0:
                    print("no tube")
                elif DIAMETER_TOLERANCES[0] < diameter <= DIAMETER_TOLERANCES[1]:
                    add_maneuver(STOCK_TUBE)
                    print("small")
                elif DIAMETER_TOLERANCES[1] < diameter <= DIAMETER_TOLERANCES[2]:
                    add_maneuver(MIDDLE_DIAM)
                    print("medium")
                elif DIAMETER_TOLERANCES[2] < diameter <= DIAMETER_TOLERANCES[3]:
                    add_maneuver(STOCK_TUBE)
                    print("big")
                diameter = 0
                last_mark_distance=total_distance
            else:
                #keep following line
                if mark_number%2==0 and mark_number!=0:
                    speed_left = NORMAL_SPEED
                    speed_right = NORMAL_SPEED
                elif sensor_values[0]:
                    speed_left = NORMAL_SPEED*(0.2-0.3)
                    speed_right = NORMAL_SPEED*(0.2+0.3)
                elif sensor_values[2]:
                    speed_left = NORMAL_SPEED*(0.2+0.3)
                    speed_right = NORMAL_SPEED*(0.2-0.3)
                else:
                    speed_left = NORMAL_SPEED
                    speed_right = NORMAL_SPEED
        else:
            next_action()

    elif state == "turning_left" or state == "turning_right":
        #turning
        if abs(start_turning_angle-angle_turned)<target_val-5:
            if state == "turning_left":
                speed_left = -TURNING_SPEED
                speed_right = TURNING_SPEED
            else:
                speed_left = TURNING_SPEED
                speed_right = -TURNING_SPEED
        else:
            next_action()

    elif state == "going_straight":
        if total_distance-last_action_distance <= target_val:
            speed_left = NORMAL_SPEED
            speed_right = NORMAL_SPEED
        else:
            next_action()

    elif state == "stop":
        if current_time - last_action_time < target_val:
            speed_left = 0
            speed_right = 0
        else:
            next_action()
    #retour
    true_speed_right, true_speed_left = simulator.get_true_speeds()
    distance_step = WHEEL_RADIUS*float(true_speed_left+true_speed_right)/2*dt
    angle_step = math.degrees(WHEEL_RADIUS*float(true_speed_left-true_speed_right)/WHEELS_SPACING*dt)

    total_distance += distance_step
    angle_turned += angle_step

    simulator.set_motor_speeds(speed_left, speed_right)

    text_to_display = ' Angle_turned: ' +str(

int(round(angle_turned))) + ' distance: ' + str(

int(round(total_distance)))+ ' diameter: ' + str(round(diameter,2)) +" state: " +state

    simulator.end_loop(text_to_display)
    time.sleep(0.05)
