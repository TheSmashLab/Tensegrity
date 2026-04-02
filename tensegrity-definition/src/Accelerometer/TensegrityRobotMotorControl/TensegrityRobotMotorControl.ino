// define pins
#define motor1slc 0
#define motor2slc 3
#define motor3slc 6
#define motor4slc 9
#define motor5slc 20
#define motor6slc 23

#define ccw 13
#define cw 14

#define motor1Pin1 1
#define motor1Pin2 2

#define motor2Pin1 4
#define motor2Pin2 5

#define motor3Pin1 7
#define motor3Pin2 8

#define motor4Pin1 10
#define motor4Pin2 11

#define motor5Pin1 18
#define motor5Pin2 19

#define motor6Pin1 21
#define motor6Pin2 22


void setup() {
    //buttons for motor select
    pinMode(motor1slc, INPUT);
    pinMode(motor2slc, INPUT);
    pinMode(motor3slc, INPUT);
    pinMode(motor4slc, INPUT);
    pinMode(motor5slc, INPUT);
    pinMode(motor6slc, INPUT);

    //Buttons for direction
    pinMode(ccw, INPUT);
    pinMode(cw, INPUT);

    // motor pin setup
    pinMode(motor1Pin1, OUTPUT);
    pinMode(motor1Pin2, OUTPUT);

    pinMode(motor2Pin1, OUTPUT);
    pinMode(motor2Pin2, OUTPUT);

    pinMode(motor3Pin1, OUTPUT);
    pinMode(motor3Pin2, OUTPUT);

    pinMode(motor4Pin1, OUTPUT);
    pinMode(motor4Pin2, OUTPUT);

    pinMode(motor5Pin1, OUTPUT);
    pinMode(motor5Pin2, OUTPUT);

    pinMode(motor6Pin1, OUTPUT);
    pinMode(motor6Pin2, OUTPUT);

}

void loop() {
  Serial.println("running");

  // put your main code here, to run repeatedly:
  while(1)
    runMotors();
}

void runMotors(){

    //motorPin1=HIGH
    //motorPin2 = LOW
    //serial.wait(1000)
    //motorPin1 = LOW
    //motorPin2 = HIGH
    //serial.wait(1000)

  //Serial.println("Running function");
  spinMotor(motor1slc, motor1Pin1, motor1Pin2, "Motor 1")
  spinMotor(motor2slc, motor2Pin1, motor2Pin2, "Motor 2")
  spinMotor(motor3slc, motor3Pin1, motor3Pin2, "Motor 3")
  spinMotor(motor4slc, motor4Pin1, motor4Pin2, "Motor 4")
  spinMotor(motor5slc, motor5Pin1, motor5Pin2, "Motor 5")
  spinMotor(motor6slc, motor6Pin1, motor6Pin2, "Motor 6")
}

void spinMotor(int whichMotor, int motorPin1, int motorPin2, String theMotor){

    if(digitalRead(whichMotor) == HIGH){

        while(digitalRead(cw) == HIGH){
          Serial.println(theMotor);
          digitalWrite(motorPin2, LOW);
          digitalWrite(motorPin1, HIGH);
        }
        while(digitalRead(ccw) == HIGH){
          digitalWrite(motorPin1, LOW);
          digitalWrite(motorPin2, HIGH);
        }
      }
      else{
        digitalWrite(motorPin1, LOW);
        digitalWrite(motorPin2, LOW);
}

//Needs:
    //Code to get motor to go in any direction
    //Automate 1 motor
    //Automate all 6 motors
    //Test different motor directions
    //add in the accelerometer
    //implement controller
