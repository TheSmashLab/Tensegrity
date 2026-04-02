#include <Arduino.h>

// Define pins
#define bottomSensor A0 // Analog pin for sensor 1
#define leftSensor A1 // Analog pin for sensor 2
#define topSensor A2 // Analog pin for sensor 3
#define rightSensor A3 // Analog pin for sensor 4
#define actuateUp 6 // Blue LED indicator
#define actuateDown 5 // Green LED indicator

// Set constant values
const float resistor = 220.0; // Resistance of resistor in series with all sensors (in ohms)
const float Vref = 5.0; // Arduino Vref
const float delayTime = 100; // 0.1 second delay (100 ms)
const int timeResolution = 1000; // 0.1 second resolution (100 ms)
const int maxTime = 10000; // 10 second maximum time
const int dataSize = maxTime / timeResolution; // Size of data arrays
const int THRESHOLD_BOTTOM = 85;
const int THRESHOLD_TOP = 65;

// Create arrays
float rBottomArray[dataSize];
float rLeftArray[dataSize];
float rTopArray[dataSize];
float rRightArray[dataSize];

void setup() {
  Serial.begin(9600);

// Set up pins
pinMode(actuateUp, OUTPUT);
pinMode(actuateDown, OUTPUT);
pinMode(bottomSensor, INPUT);
pinMode(leftSensor, INPUT);
pinMode(topSensor, INPUT);
pinMode(rightSensor, INPUT);
}

void loop() {
  int count = 0;
  float prevRBottom = 0;
  float prevRLeft = 0;
  float prevRTop = 0;
  float prevRRight = 0;
  unsigned long prevTime = millis();
  
    // Read the sensor voltages
    float vBottom = analogRead(bottomSensor) * (Vref / 1023.0);
    float vLeft = analogRead(leftSensor) * (Vref / 1023.0);
    float vTop = analogRead(topSensor) * (Vref / 1023.0);
    float vRight = analogRead(rightSensor) * (Vref / 1023.0);

    // Change voltages to resistances based on voltage divider circuit
    float rBottom = vBottom * (resistor / (Vref - vBottom));
    float rLeft = vLeft * (resistor / (Vref - vLeft));
    float rTop = vTop * (resistor / (Vref - vTop));
    float rRight = vRight * (resistor / (Vref - vRight));

    // Calculate delta resistance and delta time
    float deltaRBottom = rBottom - prevRBottom;
    float deltaRLeft = rLeft - prevRLeft;
    float deltaRTop = rTop - prevRTop;
    float deltaRRight = rRight - prevRRight;
    unsigned long deltaTime = millis() - prevTime;

    // Update previous resistance and time
    prevRBottom = rBottom;
    prevRLeft = rLeft;
    prevRTop = rTop;
    prevRRight = rRight;
    prevTime += deltaTime;

    // Put values into arrays
    rBottomArray[count] = deltaRBottom / deltaTime;
    rLeftArray[count] = deltaRLeft / deltaTime;
    rTopArray[count] = deltaRTop / deltaTime;
    rRightArray[count] = deltaRRight / deltaTime;

    // Logic to actuate motors (represented by LEDs)
    if (rBottom > THRESHOLD_BOTTOM && rTop  < THRESHOLD_TOP) {
      digitalWrite(actuateDown, HIGH);
    }
    else {
      digitalWrite(actuateDown, LOW);
    }

    if (rTop > THRESHOLD_TOP && rBottom < THRESHOLD_BOTTOM) {
      digitalWrite(actuateUp, HIGH);
    }
    else {
      digitalWrite(actuateUp, LOW);
    }

    // Code to print out delta resistance values of sensors
    Serial.print("Delta Bottom Resistance: ");
    Serial.print(rBottomArray[count]);
    Serial.print(" ohms/ms, ");
    Serial.print("Delta Top Resistance: ");
    Serial.println(rTopArray[count]);
    
    delay(delayTime);
    count += timeResolution;
  }
