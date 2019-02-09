/* http://bildr.org/2012/04/tb6612fng-arduino/
 *  http://andrewjkramer.net/motor-encoders-arduino/
 *  http://ryandowning.net/AutoPID/
 *  
*/

#include <AutoPID.h>

//motors
#define PWML 9
#define LIN1 7
#define LIN2 8
#define PWMR 10
#define RIN1 11
#define RIN2 12

//encoder
#define ENCODER_PIN_A_L 2
#define ENCODER_PIN_B_L 4
#define ENCODER_PIN_A_R 3
#define ENCODER_PIN_B_R 5
volatile unsigned long left_count = 0;
volatile unsigned long right_count = 0;

//PID
#define KP_L .12
#define KI_L .0003
#define KD_L 0
#define KP_R .12
#define KI_R .0003
#define KD_R 0
double true_speed_left, speed_left, tension_left, true_speed_right, speed_right, tension_right;
AutoPID myPID_L(&true_speed_left, &speed_left, &tension_left, -255, 255, KP_L, KI_L, KD_L);
AutoPID myPID_R(&true_speed_right, &speed_right, &tension_right, -255, 255, KP_R, KI_R, KD_R);
unsigned long last_measure_update;

//main code
#define DELTA_T 1000 // en ms
#define WHEEL_RADIUS 60 //en mm
#define NORMAL_SPEED 100 //vitesses en mm/s
#define SLOW_SPEED 40
#define TURNING_SPEED 80
long distance_step;
long distance_since_last_turn;

void setup(){
  //serial
  Serial.begin(9600);

  //motors
  pinMode(PWML, OUTPUT);
  pinMode(LIN1, OUTPUT);
  pinMode(LIN2, OUTPUT);
  //pinMode(PWMR, OUTPUT);
  //pinMode(RIN1, OUTPUT);
  //pinMode(RIN2, OUTPUT);

  //encoder
  pinMode(ENCODER_PIN_A_L,INPUT);
  pinMode(ENCODER_PIN_B_L,INPUT);
  //pinMode(ENCODER_PIN_A_R,INPUT);
  //pinMode(ENCODER_PIN_B_R,INPUT);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A_L),count_left,CHANGE);
  //attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A_R),count_right,CHANGE);

  //PID
  //myPID_L.setTimeStep(DELTA_T);
  //myPID_R.setTimeStep(DELTA_T);
}


void loop(){
  //debug
  Serial.println(left_count, right_count);
  
  //Serial.print(true_speed_left);
  //Serial.print(" ");
  //Serial.println(true_speed_right);
  
  //main code
  speed_left = NORMAL_SPEED;
  speed_right = NORMAL_SPEED;
  
  //motors PID
  //update_measured_speeds();
  //myPID_L.run();
  //myPID_R.run();
  update_motors_tension();
  
  delay(300);
}


void update_measured_speeds(){
  if ((millis() - last_measure_update) > DELTA_T) {
    true_speed_left=WHEEL_RADIUS*6283*left_count/(2940*DELTA_T);//6283=2*pi*1000 //2940=7*2*210=pulses per rotation
    true_speed_right=WHEEL_RADIUS*6283*right_count/(2940*DELTA_T);
    left_count=0;
    right_count=0;
    last_measure_update = millis();
    distance_step = (true_speed_left+true_speed_right)*DELTA_T/(2*1000);
    distance_since_last_turn += distance_step;
  }
}

void count_left() {
  if (digitalRead(ENCODER_PIN_A_L) != digitalRead(ENCODER_PIN_B_L))left_count++;
  else left_count--;
}

void count_right() {
  if (digitalRead(ENCODER_PIN_A_R) != digitalRead(ENCODER_PIN_B_R))right_count++;
  else right_count--;
}

void update_motors_tension(){
  tension_left = 128;// a enlever
  tension_right = 128;// a enlever
  boolean inPin1L = LOW;
  boolean inPin2L = HIGH;
  if(tension_left<0){
  inPin1L = HIGH;
  inPin2L = LOW;
  }
  
  boolean inPin1R = LOW;
  boolean inPin2R = HIGH;
  if(tension_right<0){
  inPin1R = HIGH;
  inPin2R = LOW;
  }
  
  digitalWrite(LIN1, inPin1L);
  digitalWrite(LIN2, inPin2L);
  analogWrite(PWML, abs(tension_left));
  
  //digitalWrite(RIN1, inPin1R);
  //digitalWrite(RIN2, inPin2R);
  //analogWrite(PWMR, abs(tension_right));
}
