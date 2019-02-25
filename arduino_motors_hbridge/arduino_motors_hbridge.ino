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
long last_left_count = 0;
long last_right_count = 0;

//breakbeam
#define BREAKBEAM_PIN 6

//line sensors
#define LINE_PIN_L A0
#define LINE_PIN_M A1
#define LINE_PIN_R A2

//PID
#define KP_L 0.000002
#define KI_L 0
#define KD_L 0
#define KP_R 0.000002
#define KI_R 0
#define KD_R 0
double true_speed_left, speed_left, true_speed_right, speed_right, delta_coef_right, delta_coef_left;
double coef_left = 0.96;
double coef_right = 1.06;
AutoPID myPID_L(&true_speed_left, &speed_left, &delta_coef_left, -255, 255, KP_L, KI_L, KD_L);
AutoPID myPID_R(&true_speed_right, &speed_right, &delta_coef_right, -255, 255, KP_R, KI_R, KD_R);
unsigned long last_measure_update;

//main code
const int DELTA_T=100; // en ms
const int WHEEL_RADIUS= 60; //en mm
const int WHEELS_SPACING = 304;
const int NORMAL_SPEED  = 250; //vitesses en mm/s
const int SLOW_SPEED  = 150;
const int TURNING_SPEED = 150;
const int TURN_AFTER_COUNT_1 = 6000*2;
const int TURN_AFTER_COUNT_2 = 2200*2;
const int START_TURN_COUNT_DELAY = 80;
const int K = 5;
unsigned long current_time = millis();
int sensor_left,sensor_middle,sensor_right, breakbeam;
int last_breakbeam = 1;
int tube_enter_count = 0;
String turning = "";
int number_of_turns = 0;
long last_turn_count = 0;
long start_turning_count = 0;

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
  //SENSORS VALUES//
  breakbeam = digitalRead(BREAKBEAM_PIN);
  sensor_left = analogRead(LINE_PIN_L);
  sensor_middle = analogRead(LINE_PIN_M);
  sensor_right = analogRead(LINE_PIN_R);
  current_time = millis();
  
  //MAIN CODE//
  
  speed_left = 200;
  speed_right = 200;
  
  long count_since_last_turn = right_count+left_count-last_turn_count;
  if(turning == "left" || turning == "right"){
    //turning
    long angle_turned = get_angle((left_count - right_count) - start_turning_count);
    Serial.println(angle_turned);
    if(0 <= count_since_last_turn <= START_TURN_COUNT_DELAY){}
    else if (angle_turned<=90 && count_since_last_turn > START_TURN_COUNT_DELAY){
      if (turning == "left"){
        speed_left = -TURNING_SPEED;
        speed_right = TURNING_SPEED;
      }
      else{
        speed_left = TURNING_SPEED;
        speed_right = -TURNING_SPEED;
      }
    }
    else{
      //stop turning
      turning = "";
      last_turn_count = right_count+left_count;
      number_of_turns+=1;
    }
  }
  else{
    //following line
    if (((count_since_last_turn>TURN_AFTER_COUNT_1 && number_of_turns % 2==0) || (count_since_last_turn>TURN_AFTER_COUNT_2 && number_of_turns % 2==1))
    && number_of_turns < 10
    && (((number_of_turns/2)%2 == 1 and sensor_right) || (number_of_turns/2)%2 == 0 and sensor_left)){
      //start turning
      Serial.println("Starting turn " + String(number_of_turns+1));
      last_turn_count = right_count+left_count;
      start_turning_count = left_count-right_count;
      if ((number_of_turns/2)%2 == 1) turning = "right";
      else turning = "left";
      }
    else{
      //keep following line
      double error = (sensor_left + sensor_middle*10 + sensor_right*20)/double( sensor_left + sensor_middle + sensor_right) - 10;
      if(abs(error)<4.5){
        //Serial.println("go straight");
        speed_left = 200;
        speed_right = 200;
      }
      else if(error<0){
        //Serial.println("go left");
        speed_left = 150;
        speed_right = 200;
      }
      else if(error>0){
        //Serial.println("go right");
        speed_left = 200;
        speed_right = 150;
      }
    }
  }
  
  if (!breakbeam && last_breakbeam) {//tube enter
    tube_enter_count = left_count+right_count;
  }
  if (breakbeam && !last_breakbeam) {//tube exit
    double diameter = get_distance(left_count+right_count-tube_enter_count)/2;
    Serial.println("Diameter: " + String(diameter));
  }
  last_breakbeam=breakbeam;
  
  //MOTORS PID//
  if ((current_time - last_measure_update) > DELTA_T) {
    update_measured_speeds(current_time - last_measure_update);
    last_measure_update = current_time;
    myPID_L.run();
    myPID_R.run();
    if(abs(true_speed_left)<100)delta_coef_left=0;//pour garder le meme coef quand l interupteur est eteint
    if(abs(true_speed_right)<100)delta_coef_right=0;
    
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
}


void update_measured_speeds(unsigned long delta_t){ // permet de connaitre la vitesse des moteurs
  true_speed_left=get_distance(left_count-last_left_count)*1000/delta_t;
  true_speed_right=get_distance(right_count-last_right_count)*1000/delta_t;
  last_left_count = left_count;
  last_right_count = right_count;
}

double get_distance(long count){ //renvoie la distance parcourue en fonction du nombre de pulses des encodeurs
  return double(WHEEL_RADIUS*2*PI*count)/2940; //2940=7*2*210=pulses par rotation
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

double update_tension(int tension, int motor){//1 for left, 0 for right
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
