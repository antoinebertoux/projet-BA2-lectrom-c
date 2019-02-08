//motors
int STBY = 10;
int PWMA = 9;
int AIN1 = 7;
int AIN2 = 8;
int PWMB = 10;
int BIN1 = 11;
int BIN2 = 12;

//encoder
long encoderValue=0;
void count(void);
void count(){encoderValue++;}

//main code
float NORMAL_SPEED = 1;
float SLOW_SPEED = 0.4;
float TURNING_SPEED = 0.8;

float speed_right;
float speed_left;


void setup(){
  //serial
  Serial.begin(9600);
  Serial.println("Started");

  //motors
  pinMode(STBY, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);

  //encoder
  encoderValue=0;
  pinMode(3,INPUT);
  attachInterrupt(digitalPinToInterrupt(3),count,FALLING);
}


void loop(){
  //debug
  Serial.println(encoderValue);

  //main code
  speed_left = NORMAL_SPEED;
  speed_right = NORMAL_SPEED;

  //motors
  set_motors_speed(speed_left, speed_right);

  delay(300);
}


void set_motors_speed(float speed_l, float speed_r){
  digitalWrite(STBY, HIGH);
  
  boolean inPin1L = LOW;
  boolean inPin2L = HIGH;
  if(speed_l<0){
  inPin1L = HIGH;
  inPin2L = LOW;
  }
  
  boolean inPin1R = LOW;
  boolean inPin2R = HIGH;
  if(speed_r<0){
  inPin1R = HIGH;
  inPin2R = LOW;
  }
  
  digitalWrite(AIN1, inPin1L);
  digitalWrite(AIN2, inPin2L);
  analogWrite(PWMA, int(max(1,abs(speed_l))*255));
  
  digitalWrite(BIN1, inPin1R);
  digitalWrite(BIN2, inPin2R);
  analogWrite(PWMB, int(max(1,abs(speed_r))*255));
}

void stop(){
digitalWrite(STBY, LOW);
}
