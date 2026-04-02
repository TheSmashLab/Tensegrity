/*
Author: David Hill
Date: July 11, 2023
Description: This file is meant to test that the ADC on the Tactile Sensor Slave board is working
properly. To use this script, upload it to an arduino due that has the Tactile Sensor Master shield
attached. Connect the master board to the slave board you wish to test via an ethernet cable. Also
connect the SS pin on the slave board to the CS1 slot on the master board. The slave board should
power on as indicated by the green power LED. The ADC actually has two channels for redundancy. The
channel is selected using a jumper between three pins. You can apply various voltages to the input
of the ADC using the V_DIV via hole nearby it on the board. This script will output the raw data
from 0 to 4096, that value converted to voltage, and the time each SPI data transfer takes in
microseconds.
*/

#include "spi_dh.h"

#define ADC_SS_PIN 33  //GPIO start pin number ss1 -> 33, ss2 -> 34 ... ss9 -> 41
#define ADC_SS_PIN_SHIFT 1  //each additional SS pin is one bit over
#define SPI_PIN 4 //dummy spi SS pin
#define CLOCK_DIVIDER 2 //defines the SPI clock = 84MHz/CLOCK_DIVIDER
#define BAUDRATE 115200 //dummy baudrate for native USB

void setup() {
  pinMode(ADC_SS_PIN, OUTPUT);  //inizialize SS pin
  REG_PIOC_SODR = 1 << ADC_SS_PIN_SHIFT;  //set to high
  SPI.begin(SPI_PIN); //begin SPI bus
  SPI.setClockDivider(SPI_PIN, CLOCK_DIVIDER);  //set the clock divider to change the frequency
  
  Serial.begin(BAUDRATE); //start serial communication
}

void loop() {
  unsigned long init_time = micros(); //start time of SPI transfer
  
  REG_PIOC_CODR = 1 << ADC_SS_PIN_SHIFT; //turn correct SS pin low (read SAM3X datasheet section 31)

	SPI.spi->SPI_TDR = SPI_PCS(1) | SPI_TDR_LASTXFER; //initiate SPI data transfer
  while ((SPI.spi->SPI_SR & SPI_SR_RDRF) == 0); //wait while the SPI data is being retreived

	uint16_t data = (uint16_t) SPI.spi->SPI_RDR & 0x0FFF; //read data

  REG_PIOC_SODR = 1 << ADC_SS_PIN_SHIFT; //turn correct SS pin high (read SAM3X datasheet section 31)
  
  unsigned long end_time = micros();  //end time of SPI transfer

  Serial.print("Raw: ");  //print out the raw data (0 - 4095)
  Serial.print(data);
   
  float voltage = float(data) / pow(2,12) * 3.3;  //convert to voltage

  Serial.print(",  \t Voltage: ");  //print out the voltage
  Serial.print(voltage);
  Serial.print(",  \t Time: ");   //print out the time the transfer took in microseconds (should be about 3)
  Serial.println(end_time - init_time);

  delay(100); //delay so it's not running very fast
}
