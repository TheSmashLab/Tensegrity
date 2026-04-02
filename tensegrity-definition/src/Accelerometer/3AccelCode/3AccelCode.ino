#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_MMA8451.h>


/* Assign a unique ID to this sensor at the same time */
Adafruit_MMA8451 mma0 = Adafruit_MMA8451(0);
Adafruit_MMA8451 mma1 = Adafruit_MMA8451(1);
Adafruit_MMA8451 mma2 = Adafruit_MMA8451(2);

// Select I2C BUS
void TCA9548A(uint8_t bus){
  Wire.beginTransmission(0x70);  // TCA9548A address
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
  Serial.print(bus);
}


void setup(void) 
{
  Serial.begin(9600);
  Serial.println("Accelerometer test"); Serial.println("");
  Wire.begin();
  /* Initialise the 1st sensor */
  TCA9548A(0);
  if(!mma0.begin())
  {
    Serial.println("No mma0 detected");
    while(1);
  }
  
  /* Initialise the 2nd sensor */
  TCA9548A(1);
  if(!mma1.begin())
  {
    /* There was a problem detecting the HMC5883 ... check your connections */
    Serial.println("No mma1 detected");
    while(1);
  }
  /* Initialise the 2nd sensor */
  TCA9548A(2);
  if(!mma2.begin())
  {
    /* There was a problem detecting the HMC5883 ... check your connections */
    Serial.println("No mma2 detected");
    while(1);
  }
    
}

void loop(void) 
{
  /* Get a new sensor event */ 
  sensors_event_t event; 
  
  TCA9548A(0);
  mma0.getEvent(&event);
 
  /* Display the results (acceleration is measured in m/s^2) */
  Serial.println("Accel 1:");
  Serial.print("X: \t"); Serial.print(event.acceleration.x); Serial.print("\t");
  Serial.print("Y: \t"); Serial.print(event.acceleration.y); Serial.print("\t");
  Serial.print("Z: \t"); Serial.print(event.acceleration.z); Serial.print("\t");
  Serial.println("m/s^2 ");
  
  TCA9548A(1);
  mma1.getEvent(&event);
 
  /* Display the results (acceleration is measured in m/s^2) */
  Serial.println("Accel 2:");
  Serial.print("X: \t"); Serial.print(event.acceleration.x); Serial.print("\t");
  Serial.print("Y: \t"); Serial.print(event.acceleration.y); Serial.print("\t");
  Serial.print("Z: \t"); Serial.print(event.acceleration.z); Serial.print("\t");
  Serial.println("m/s^2 ");

  TCA9548A(2);
  mma2.getEvent(&event);
 
  /* Display the results (acceleration is measured in m/s^2) */
  Serial.println("Accel 3:");
  Serial.print("X: \t"); Serial.print(event.acceleration.x); Serial.print("\t");
  Serial.print("Y: \t"); Serial.print(event.acceleration.y); Serial.print("\t");
  Serial.print("Z: \t"); Serial.print(event.acceleration.z); Serial.print("\t");
  Serial.println("m/s^2 ");

  delay(2000);
}