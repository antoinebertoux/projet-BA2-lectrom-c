/* http://bildr.org/2012/04/tb6612fng-arduino/
 *  http://andrewjkramer.net/motor-encoders-arduino/
 *  http://ryandowning.net/AutoPID/
 *  https://www.arduino.cc/en/Reference/Servo
*/

#include <AutoPID.h>
#include <Servo.h>

//motors
#define PWML 9
#define LIN1 7
#define LIN2 8
#define PWMR 6
#define RIN1 11
#define RIN2 12

//encoder
#define ENCODER_PIN_A_L 2
#define ENCODER_PIN_B_L 4
#define ENCODER_PIN_A_R 3
#define ENCODER_PIN_B_R 5
volatile long left_count = 0;
volatile long right_count = 0;
long last_left_count = 0;
long last_right_count = 0;

//breakbeam
#define BREAKBEAM_PIN A3

//line sensors
#define LINE_PIN_L A0
#define LINE_PIN_M A1
#define LINE_PIN_R A2

//servo
#define SERVO_PIN 10
int servo_angle = 0;
Servo servo; 

//PID
#define KP_L 0.000002
#define KI_L 0
#define KD_L 0
#define KP_R 0.000002
#define KI_R 0
#define KD_R 0
double true_speed_left, speed_left, true_speed_right, speed_right, delta_coef_right, delta_coef_left;
double coef_left = 0.9;
double coef_right = 0.81;
AutoPID myPID_L(&true_speed_left, &speed_left, &delta_coef_left, -255, 255, KP_L, KI_L, KD_L);
AutoPID myPID_R(&true_speed_right, &speed_right, &delta_coef_right, -255, 255, KP_R, KI_R, KD_R);
unsigned long last_measure_update;

//main code
#define FOLLOWING_LINE 0
#define TURNING_LEFT 1
#define TURNING_RIGHT 2
#define GOING_STRAIGHT 3
#define ROTATE_SERVO 4
#define STOP 5
const int DELTA_T=100; // en ms
const int WHEEL_DIAMETER= 70; //en mm
const int WHEELS_SPACING = 310;
const int NORMAL_SPEED  = 130; //vitesses en mm/s
const int SLOW_SPEED  = 100;
const int TURNING_SPEED = 150;
const int TURN_AFTER_DISTANCE_1 = 820;
const int TURN_AFTER_DISTANCE_2 = 310;
const int K = 22;
const int LINE_SENSOR_TOLERANCE = 700;
unsigned long current_time = millis();
unsigned long last_servo_update = millis();
unsigned long last_action_time = millis();
int sensor_left,sensor_middle,sensor_right, breakbeam;
int last_breakbeam = 1;
long tube_enter_count = 0;
int mark_number = 0;
long last_turn_count = 0;
long start_turning_count = 0;
int state = FOLLOWING_LINE;
long target_val = 0;
int action_list[20][2];
int action_number = 0;
bool last_on_mark = false;
double diameter = 0;

int RETURN[][2] = {{STOP,10000}};
int LEFT_TURN[][2] = {{TURNING_LEFT, 90}};
int RIGHT_TURN[][2] = {{TURNING_RIGHT, 90}};

void setup(){
  //serial
  Serial.begin(9600);

  //motors
  pinMode(PWML, OUTPUT);
  pinMode(LIN1, OUTPUT);
  pinMode(LIN2, OUTPUT);
  pinMode(PWMR, OUTPUT);
  pinMode(RIN1, OUTPUT);
  pinMode(RIN2, OUTPUT);

  //encoder
  pinMode(ENCODER_PIN_A_L,INPUT);
  pinMode(ENCODER_PIN_B_L,INPUT);
  pinMode(ENCODER_PIN_A_R,INPUT);
  pinMode(ENCODER_PIN_B_R,INPUT);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A_L),increment_left_count,CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A_R),increment_right_count,CHANGE);

  //servo
  //servo.attach(SERVO_PIN);
  //servo.write(0);
  
  //Breakbeam
  pinMode(BREAKBEAM_PIN, INPUT_PULLUP);
  
  //line sensors
  pinMode(LINE_PIN_L, INPUT);
  pinMode(LINE_PIN_M, INPUT);
  pinMode(LINE_PIN_R, INPUT);
  
  //PID
  myPID_L.setTimeStep(DELTA_T);
  myPID_R.setTimeStep(DELTA_T);
}

void loop(){
  //SENSORS VALUES//
  breakbeam = digitalRead(BREAKBEAM_PIN);
  sensor_left = analogRead(LINE_PIN_L) > LINE_SENSOR_TOLERANCE;
  sensor_middle = analogRead(LINE_PIN_M) > LINE_SENSOR_TOLERANCE;
  sensor_right = analogRead(LINE_PIN_R) > LINE_SENSOR_TOLERANCE;
  current_time = millis();
  
  //MAIN CODE//

  state = action_list[action_number][0];
  target_val = action_list[action_number][1];
  
  speed_left = NORMAL_SPEED;
  speed_right = NORMAL_SPEED;
  //174
  //Serial.println(get_distance((right_count+left_count)/2));
  
  if(state == FOLLOWING_LINE){
    long distance_since_last_turn = get_distance(right_count+left_count-last_turn_count)/2;
    if(get_distance(left_count+right_count-last_turn_count)/2 < target_val || target_val == 0){
      if(sensor_left && sensor_right){
        if(!last_on_mark){
          if(mark_number >= 11)set_maneuver(RETURN, sizeof(RETURN));
          else if(((mark_number-1)/2)%2 == 0)set_maneuver(LEFT_TURN, sizeof(LEFT_TURN));
          else set_maneuver(RIGHT_TURN, sizeof(RIGHT_TURN));
          mark_number++;
          Serial.println(mark_number);
          
          if (diameter == 0)Serial.println("No tube");
          else Serial.println("Diameter: " + String(diameter));//add_maneuver(STOCK_TUBE, sizeof(STOCK_TUBE))
          diameter = 0;
          }
        last_on_mark = true;
        }
      else{
        last_on_mark = false;
        //keep following line
        //double error = (sensor_left + sensor_middle*10 + sensor_right*20)/double(sensor_left + sensor_middle + sensor_right) - 10;
        //Serial.println(error);
        if (mark_number%2==0 and mark_number!=0){
          //straight from one line to another
          speed_left = NORMAL_SPEED;
          speed_right = NORMAL_SPEED;
        }
        else if (sensor_left){
          //turn_right
          speed_left = NORMAL_SPEED*(0.2-0.3);
          speed_right = NORMAL_SPEED*(0.2+0.3);
        }
        else if (sensor_right){
          //turn_left
          speed_left = NORMAL_SPEED*(0.2+0.3);
          speed_right = NORMAL_SPEED*(0.2-0.3);     
        }
        else{
          //on line
          speed_left = NORMAL_SPEED;
          speed_right = NORMAL_SPEED;
        }
      }
    }
    else{
      next_action();
    }
  }

  else if(state == TURNING_LEFT || state == TURNING_RIGHT){
    long angle_turned = get_angle((left_count - right_count) - start_turning_count);
    //Serial.println(angle_turned);
    if (abs(angle_turned)<=target_val){
      if (state == TURNING_LEFT){
        speed_left = -TURNING_SPEED;
        speed_right = TURNING_SPEED;
      }
      else{
        speed_left = TURNING_SPEED;
        speed_right = -TURNING_SPEED;
      }
    }
    else{
      next_action();
    }
  }
  
  else if(state == GOING_STRAIGHT){
    if(get_distance(left_count+right_count-last_turn_count)/2 < target_val){
      speed_left = NORMAL_SPEED;
      speed_right = NORMAL_SPEED;
    }

    else{
      next_action();
    }
    
  }

  else if(state == ROTATE_SERVO){
    if(current_time - last_servo_update > 20){
      if(servo_angle<target_val)servo_angle++;
      else if (servo_angle>target_val)servo_angle--;
      else next_action();
      last_servo_update = current_time;
    }
  }
  
  else if(state == STOP){
    if(current_time-last_action_time < target_val){
      speed_left = 0;
      speed_right = 0;
    }
    else{
      next_action();
    }
  }

  
  if (!breakbeam && last_breakbeam) {//tube enter
    tube_enter_count = left_count+right_count;
  }
  if (breakbeam && !last_breakbeam) {//tube exit
    diameter = get_distance(left_count+right_count-tube_enter_count)/2;
  }
  last_breakbeam=breakbeam;
  //MOTORS PID//
  if ((current_time - last_measure_update) > DELTA_T) {
    update_measured_speeds(current_time - last_measure_update);
    last_measure_update = current_time;
    if(state == FOLLOWING_LINE){
      myPID_L.run();
      myPID_R.run();
    }
    if(abs(true_speed_left)<70||abs(true_speed_right)<70 || state != FOLLOWING_LINE){
      delta_coef_left=0;//pour garder le meme coef quand l interupteur est eteint
      delta_coef_right=0;
    }
    //DEBUG//
    //Serial.print(true_speed_left);
    //Serial.print(" ");
    //Serial.println(true_speed_right);
    
    //Serial.print(String(sensor_left)+" ");
    //Serial.print(String(sensor_middle)+" ");
    //Serial.println(String(sensor_right)+" ");
    
    //Serial.print(String(coef_left)+" ");
    //Serial.print(String(coef_right)+" ");
    //Serial.print(String(true_speed_left)+" ");
    //Serial.println(String(true_speed_right)+" ");
  }
  update_motors_tension();
  //servo.write(servo_angle);
}

void next_action(){
  action_number++;
  last_turn_count = left_count+right_count;
  start_turning_count = left_count-right_count;
}


void set_maneuver(int maneuver[][2], int n){
  for(int i = 0; i<20;i++){
    if(i<n){
      action_list[i][0] = maneuver[i][0];
      action_list[i][1] = maneuver[i][1];
    }
    else{
      action_list[i][0] = 0;
      action_list[i][1] = 0;
    }
  }
  next_action();
  action_number = 0;
}

void add_maneuver(int maneuver[][2], int n){
  int j=0;
  int i=0;
  while(j<n){
    if(action_list[i][0] == 0){
      action_list[i][0] = maneuver[j][0];
      action_list[i][1] = maneuver[j][1];
      j++;
    }
    i++;
  }
}


void update_measured_speeds(unsigned long delta_t){ // permet de connaitre la vitesse des moteurs
  true_speed_left=get_distance(left_count-last_left_count)*1000/delta_t;
  true_speed_right=get_distance(right_count-last_right_count)*1000/delta_t;
  last_left_count = left_count;
  last_right_count = right_count;
}

double get_distance(long count){ //renvoie la distance parcourue en fonction du nombre de pulses des encodeurs
  return double(WHEEL_DIAMETER*PI*count)/2940; //2940=7*2*210=pulses par rotation
}
double get_angle(long count){//renvoie l'angle tourné en fonction de la difference du nombre de pulse (L-R)
  return (get_distance(count)/WHEELS_SPACING)*180/PI;
}
void increment_left_count() {
  if (digitalRead(ENCODER_PIN_A_L) != digitalRead(ENCODER_PIN_B_L))left_count--; // permet de connaitre le sens de rotation du moteur gauche
  else left_count++;
}

void increment_right_count() {
  if (digitalRead(ENCODER_PIN_A_R) != digitalRead(ENCODER_PIN_B_R))right_count++; // permet de connaitre le sens de rotation du moteur droit
  else right_count--;
}

void update_motors_tension(){
  coef_left+=delta_coef_left; //delta_coef_left et right sont donnés par le PID
  coef_right+=delta_coef_right;
  update_tension(speed_left*coef_left, 0);
  update_tension(speed_right*coef_right, 1);
}

void update_tension(int tension, int motor){//1 for left, 0 for right
  if (tension>255)tension = 255;
  if (tension<-255)tension = -255;
  boolean inPin1 = LOW;
  boolean inPin2 = HIGH;
  if(tension<0){
  inPin1 = HIGH;
  inPin2 = LOW;
  }
  if(motor == 1){
  digitalWrite(LIN1, inPin1);
  digitalWrite(LIN2, inPin2);
  analogWrite(PWML, abs(tension));
  }else{
  digitalWrite(RIN1, inPin1);
  digitalWrite(RIN2, inPin2);
  analogWrite(PWMR, abs(tension));
  }
}
