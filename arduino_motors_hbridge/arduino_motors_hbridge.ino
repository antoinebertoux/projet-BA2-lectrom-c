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
volatile long left_count = 0;
volatile long right_count = 0;

//breakbeam
#define BREAKBEAM_PIN 13

//line sensors
#define LINE_PIN_L A0
#define LINE_PIN_M A1
#define LINE_PIN_R A2

//PID
#define KP_L .25
#define KI_L .0003
#define KD_L 300
#define KP_R .25
#define KI_R .0003
#define KD_R 300
double true_speed_left, speed_left, tension_left, true_speed_right, speed_right, tension_right, delta_tension_right, delta_tension_left;
AutoPID myPID_L(&true_speed_left, &speed_left, &delta_tension_left, -255, 255, KP_L, KI_L, KD_L);
AutoPID myPID_R(&true_speed_right, &speed_right, &delta_tension_right, -255, 255, KP_R, KI_R, KD_R);
unsigned long last_measure_update;

//main code
double distance_step_left, distance_step_right, distance_step, distance_since_last_turn;
int DELTA_T=500; // en ms
int WHEEL_RADIUS= 60; //en mm
int NORMAL_SPEED  = 250; //vitesses en mm/s
int SLOW_SPEED  = 150;
int TURNING_SPEED = 150;
unsigned long start_time = millis();
unsigned long current_time = millis();
int sensor_left,sensor_middle,sensor_right, breakbeam;

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
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A_L),increment_left_count,FALLING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A_R),increment_right_count,FALLING);

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
  //sensors values
  breakbeam = digitalRead(BREAKBEAM_PIN);
  sensor_left = analogRead(LINE_PIN_L);
  sensor_middle = analogRead(LINE_PIN_M);
  sensor_right = analogRead(LINE_PIN_R);

  current_time = millis();
  
  //main code
  //speed_left = NORMAL_SPEED*sin((millis()-start_time)/10000.0);
  speed_left = SLOW_SPEED;
  speed_right = SLOW_SPEED;
  
  //motors PID
  if ((current_time - last_measure_update) > DELTA_T) {
    update_measures(DELTA_T);
    last_measure_update = current_time;
    
    //debug
    //Serial.println(left_count, right_count);
    Serial.print(true_speed_left);
    Serial.print(" ");
    Serial.println(true_speed_right);
  }
  myPID_L.run();
  myPID_R.run();
  update_motors_tension();
  delay(300)
}


void update_measures(unsigned long delta_t){ // permet de connaitre la vitesse de rotation des moteurs
  distance_step_left = WHEEL_RADIUS*2*PI*left_count/2940; //2940=7*2*210=pulses par rotation
  distance_step_right = WHEEL_RADIUS*2*PI*right_count/2940; 
  true_speed_left=distance_step_left*1000/delta_t;
  true_speed_right=distance_step_right*1000/delta_t;
  left_count=0;
  right_count=0;
  distance_step = (distance_step_left+distance_step_right)/2; // mesure la distance parcourue pendant delta t
  distance_since_last_turn += distance_step; // mesure la distance total parcourue
}

void increment_left_count() {
  if (digitalRead(ENCODER_PIN_A_L) != digitalRead(ENCODER_PIN_B_L))left_count--; // permet de connaitre le sens de rotation du moteur gauche
  else left_count++;
}

void increment_right_count() {
  if (digitalRead(ENCODER_PIN_A_R) != digitalRead(ENCODER_PIN_B_R))right_count--; // permet de connaitre le sens de rotation du moteur droit
  else right_count++;
}

void update_motors_tension(){
  tension_left = update_tension(tension_left+delta_tension_left, 1); //delta_tension_left et right sont donnés par le PID
  tension_right = update_tension(tension_right+delta_tension_right, 0);
}

double update_tension(int tension, int motor //1 for left, 0 for right){
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
  return tension;
}
