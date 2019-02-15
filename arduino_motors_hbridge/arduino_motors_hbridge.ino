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
#define BREAKBEAM_PIN 12

//line sensors
#define LINE_PIN_L A0
#define LINE_PIN_M A1
#define LINE_PIN_R A2

//PID
#define KP_L .3
#define KI_L .0003
#define KD_L 300
#define KP_R .12
#define KI_R .0003
#define KD_R 0
double true_speed_left, speed_left, tension_left, true_speed_right, speed_right, tension_right, delta_tension_right, delta_tension_left;
AutoPID myPID_L(&true_speed_left, &speed_left, &delta_tension_left, -255, 255, KP_L, KI_L, KD_L);
AutoPID myPID_R(&true_speed_right, &speed_right, &delta_tension_right, -255, 255, KP_R, KI_R, KD_R);
unsigned long last_measure_update;

//main code
long DELTA_T=500; // en ms
long WHEEL_RADIUS= 60; //en mm
#define NORMAL_SPEED 200 //vitesses en mm/s
#define SLOW_SPEED 40
#define TURNING_SPEED 80
long distance_step;
long distance_since_last_turn;
long start_time = millis();
int sensor_left,sensor_middle,sensor_right;
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
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A_L),count_left,FALLING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A_R),count_right,FALLING);

  //Breakbeam
  pinMode(BREAKBEAM_PIN, INPUT);
  digitalWrite(BREAKBEAM_PIN, HIGH);

  //line sensors
  pinMode(LINE_PIN_L, INPUT);
  pinMode(LINE_PIN_M, INPUT);
  pinMode(LINE_PIN_R, INPUT);
  
  //PID
  myPID_L.setTimeStep(DELTA_T);
  myPID_R.setTimeStep(DELTA_T);
}


void loop(){
  //debug
  //Serial.println(left_count, right_count);
  Serial.print(true_speed_left);
  Serial.print(" ");
  Serial.println(true_speed_right);
  //Serial.println(digitalRead(BREAKBEAM_PIN));
  
   //sensor_left = analogRead(LINE_PIN_L);
   //sensor_middle = analogRead(LINE_PIN_M);
   //sensor_right = analogRead(LINE_PIN_R);
  //Serial.println(analogRead(LINE_PIN_L));
  //main code
  //speed_left = NORMAL_SPEED*sin((millis()-start_time)/10000.0);
  speed_left = 100;
  speed_right = 100;
  
  //motors PID
  update_measured_speeds();
  myPID_L.run();
  myPID_R.run();
  update_motors_tension();
  
  delay(300);
}


void update_measured_speeds(){ // permet de connaitre la vitesse de rotation des moteurs
  if ((millis() - last_measure_update) > DELTA_T) {
    true_speed_left=WHEEL_RADIUS*6283*left_count/(2940*DELTA_T);//6283=2*pi*1000 //2940=7*2*210=pulses par rotation
    true_speed_right=WHEEL_RADIUS*6283*right_count/(2940*DELTA_T);
    left_count=0;
    right_count=0;
    last_measure_update = millis();
    distance_step = (true_speed_left+true_speed_right)*DELTA_T/(2*1000); // mesure la distance parcourue pendant delta t
    distance_since_last_turn += distance_step; // mesure la distance total parcourue
  }
}

void count_left() {
  if (digitalRead(ENCODER_PIN_A_L) != digitalRead(ENCODER_PIN_B_L))left_count--; // permet de connaitre le sens de rotation du moteur gauche
  else left_count++;
}

void count_right() {
  if (digitalRead(ENCODER_PIN_A_R) != digitalRead(ENCODER_PIN_B_R))right_count++; // permet de connaitre le sens de rotation du moteur droit
  else right_count--;
}

void update_motors_tension(){
  tension_left = update_tension(tension_left+delta_tension_left, 1);
  tension_right = update_tension(tension_right+delta_tension_right, 0);
}

double update_tension(int tension, int motor){
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
  analogWrite(PWML, abs(100));
  }else{
  digitalWrite(RIN1, inPin1);
  digitalWrite(RIN2, inPin2);
  analogWrite(PWMR, abs(100));
  }
  return tension;
}
