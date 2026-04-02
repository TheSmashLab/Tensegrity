/*
Author: David Hill
Date: July 11, 2023
Description: This file is meant to test the 12-bit binary counter and LED's on the Tactile Sensor Slave board.
It will trigger the counter repeatedly so that someone can visually ensure that it and the LED's are working.
To use this script, connect an ethernet cable between the Tactile Sensor Master board and the Tactile Sensor
Slave board. The master board should be atop an Arduino Due which should be loaded with this code file. Once
loaded, the file will wait five seconds than start incrementing the counter. On the slave board, the 10 blue
LED's should start flashing. They should be counting in binary in this order: RO, R1, R2, R3, C0, C1, C2, C3,
C4, C5. If you notice that one of the LED's is not lighting up, then there is either a problem with that LED
or a short somewhere on the line. Read the README file in this directory for more information.
*/

#define COUNT_PIN 53  //pins used for count and clear operations
#define CLR_PIN 52

void reset_counter(){ //function to reset the counter
  digitalWrite(CLR_PIN, HIGH);  //use clear pin to reset
  delayMicroseconds(1);
  digitalWrite(CLR_PIN, LOW);
}

void increment_counter(){ //function to increment the counter
  digitalWrite(COUNT_PIN, HIGH);  //use count pin to increment
  delayMicroseconds(1);
  digitalWrite(COUNT_PIN, LOW);
}

void setup() {
  pinMode(COUNT_PIN, OUTPUT);   //set the count pin mode and initialize it to LOW
  digitalWrite(COUNT_PIN, LOW);
  pinMode(CLR_PIN, OUTPUT); //set the clear pin mode
  reset_counter();  //set the counter to zero (all blue LED's should be off)
  delay(5000);  //wait five seconds
}

void loop() {
  increment_counter();  //increment counter
  delay(10);  //delay 10 milliseconds so visible (should take ~10 seconds to run through all 1024 LED states)
}
