/*
Author: David Hill
Date: July 11, 2023
Description: This file is meant to pull data from a series of tactile sensing sleeves on an SPI bus.
Along with the SPI bus, each sleeve is connected to count and clear pins. The count pin triggers all
the sleeves to move to the next sensor. The clear pin triggers all the sleeves to move to the first
sensor. This file will only run correctly if it is placed in the same directory as spi_dh.h and spi_dh.cpp.
These are files based on the standard arduino due spi library, modified for increased speed.
To understand everything in this file, the SAM3X datasheet is helpful:
https://ww1.microchip.com/downloads/en/devicedoc/atmel-11057-32-bit-cortex-m3-microcontroller-sam3x-sam3a_datasheet.pdf
It is also available in the resources folder of the tactile_sensor repository.
Also, the Arduino Due SPI library: https://github.com/arduino/ArduinoCore-sam/blob/master/libraries/SPI/src/SPI.cpp
*/

#include "spi_dh.h"
#include <stdlib.h>

#define ADC_SS_PIN_NUBMER_START 33  //GPIO start pin number ss1 -> 33, ss2 -> 34 ... ss9 -> 41
#define ADC_SS_PIN_SHIFT_START 1  //each additional SS pin is one bit over
#define SPI_PIN 4 //dummy spi SS pin
#define CLOCK_DIVIDER 4 //defines the SPI clock = 84MHz/CLOCK_DIVIDER
#define BAUDRATE 115200 //dummy baudrate for native USB
// #define DATA_MASK 0x1FFE
// #define DATA_MASK 0x0FFF  //assume no delay in line (line must be less than CLOCK_DIVIDER*1.19 meters long)
// #define DATA_SHIFT 1
// #define DATA_SHIFT 0  //assume no delay in line (line must be less than CLOCK_DIVIDER*1.19 meters long)
#define SENSOR_SEL_PIN_NUMBER_START 25
#define MAX_SENSOR_NUMBER 8

#define COUNT_PIN 53  //GPIO pin for count
#define COUNT_PIN_SHIFT 14  //shift ammount in PIOB registers
#define TOGGLE_COUNT_PIN REG_PIOB_SODR = 1 << COUNT_PIN_SHIFT; REG_PIOB_CODR = 1 << COUNT_PIN_SHIFT;  //command to turn on and off count pin

#define CLEAR_PIN 52  //GPIO pin for clear
#define CLEAR_PIN_SHIFT 21  //shift ammount in PIOB registers
#define TOGGLE_CLEAR_PIN REG_PIOB_SODR = 1 << CLEAR_PIN_SHIFT; REG_PIOB_CODR = 1 << CLEAR_PIN_SHIFT;  //command to turn on and off clear pin

#define NUM_ROWS 16 //number of rows in sleeves
#define ROW_INDEXES {1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14}  //defines the order in which the rows are read
#define NUM_COLUMNS 64  //number of columns in sleeves
//defines the order in which the columns are read
#define COLUMN_INDEXES {0, 16, 32, 48, 1, 17, 33, 49, 2, 18, 34, 50, 3, 19, 35, 51, 4, 20, 36, 52, 5, 21, 37, 53, 6, 22, 38, 54, 7, 23, 39, 55, 8, 24, 40, 56, 9, 25, 41, 57, 10, 26, 42, 58, 11, 27, 43, 59, 12, 28, 44, 60, 13, 29, 45, 61, 14, 30, 46, 62, 15, 31, 47, 63}
#define TAXILES_PER_SLEEVE NUM_ROWS * NUM_COLUMNS //number of taxiles per sleeve
#define MAX_MESSAGE_LENGTH MAX_SENSOR_NUMBER * (TAXILES_PER_SLEEVE + 1) + 2 //total number of sensors

#define END_BYTES 0xFFFF //end byte should never show up in the bytes that are read in

const uint8_t row_indexes[NUM_ROWS] = ROW_INDEXES;  //defines the order in which the rows are read
const uint8_t column_indexes[NUM_COLUMNS] = COLUMN_INDEXES; //defines the order in which the columns are read

uint8_t num_sleeves = 0;  //actual number of sleeves we are reading
uint16_t message_length = 0;  //actual message length based on how many sleeves we are reading
uint8_t header_length = 0;  //actual header length based on how many sleeves we are reading
uint8_t sleeve_ids[MAX_SENSOR_NUMBER];  //id of each sleeve we are reading based on CS pin and determined by switches selected on the board

bool update_cs = false; //this flag is used to update which sensors we are reporting

volatile uint16_t buf[MAX_MESSAGE_LENGTH];  //message buffer

void setup() {
  for(int i = 0; i < MAX_SENSOR_NUMBER; i++){  //initialize SS pins
    pinMode(ADC_SS_PIN_NUBMER_START + i, OUTPUT); //set mode to output
    REG_PIOC_SODR = 1 << (ADC_SS_PIN_SHIFT_START + i);  //set to high
  }

  SPI.begin(SPI_PIN); //begin SPI bus
  SPI.setClockDivider(SPI_PIN, CLOCK_DIVIDER);  //set the clock divider to change the frequency

  pinMode(COUNT_PIN, OUTPUT); //set the count pin mode
  digitalWrite(COUNT_PIN, LOW); //set the count pin to low

  pinMode(CLEAR_PIN, OUTPUT); //set the clear pin mode
  Serial.begin(BAUDRATE); //begin regular serial
  SerialUSB.begin(BAUDRATE);  //begin native USB serial communication (for fast data transmission)

  for(int i = 0; i < MAX_SENSOR_NUMBER; i++){ //for each pin connected to a switch on the board
    pinMode(SENSOR_SEL_PIN_NUMBER_START + i, INPUT_PULLUP); //set the pin mode to input with a pullup resistor
    attachInterrupt(digitalPinToInterrupt(SENSOR_SEL_PIN_NUMBER_START + i), cs_update, CHANGE); //attach a CHANGE interrupt to each pin, see cs_update()
  }

  update_cs = true; //at the start, update which sensors we are reporting

  delay(10);  //give time to settle before starting
  TOGGLE_CLEAR_PIN  //start the sensors at zero
}

void loop() {
  if(update_cs){  //if we are just starting or a change in the cs switches was detected
    update_cs = false;  //disable the update_cs flag so it isn't called in the next loop

    num_sleeves = 0;  //initiate sleeve number at zero
    for(int i = 0; i < MAX_SENSOR_NUMBER; i++){ //for each switch
      if(!digitalRead(SENSOR_SEL_PIN_NUMBER_START + i)){  //if the switch is enabled
        sleeve_ids[num_sleeves] = i;  //add the id to the sleeve_ids array
        num_sleeves++;  //increment the number of sleeves we are reporting
      }
    }

    message_length = num_sleeves * (TAXILES_PER_SLEEVE + 1) + 2;  //update the message size we are sending
    header_length = 2 + num_sleeves;

    buf[0] = END_BYTES; //add start byte to buffer
    buf[1] = (uint16_t) num_sleeves; //add the number of sleeves we are reporting

    for(int i = 0; i < num_sleeves; i++){ //fill the rest of the header with the sleeve ID's
      buf[2 + i] = sleeve_ids[i];
    }

    for(int i = 0; i < num_sleeves * TAXILES_PER_SLEEVE; i++){  //inisialize buffer with zeros
      buf[header_length + i] = 0;
    }

    Serial.print("Sensor Count Updated: "); //debug statement
    Serial.println(num_sleeves);
  }

  for(int i = 0; i < NUM_COLUMNS; i++){ //for every column
    uint16_t column_shift = column_indexes[i]*NUM_ROWS; //define column_shift
    for(int j = 0; j < NUM_ROWS; j++){  //for every row
      uint8_t row_shift = row_indexes[j]; //define row_shift
      for(int k = 0; k < num_sleeves; k++){ //for every sensor
        REG_PIOC_CODR = 1 << (ADC_SS_PIN_SHIFT_START + sleeve_ids[k]);  //turn correct SS pin low (read SAM3X datasheet section 31)
        //this is based on spi_dh.cpp lines 175-190 (it is a bit faster if you do it here rather than calling a function)
        SPI.spi->SPI_TDR = SPI_PCS(1) | SPI_TDR_LASTXFER; //initiate SPI data transfer
        while ((SPI.spi->SPI_SR & SPI_SR_RDRF) == 0); //wait while the SPI data is being retreived
        // buf[row_shift + column_shift + k*TAXILES_PER_SLEEVE] = (uint16_t) (SPI.spi->SPI_RDR & DATA_MASK) >> DATA_SHIFT;  //set the data
        buf[header_length + row_shift + column_shift + k*TAXILES_PER_SLEEVE] = (uint16_t) SPI.spi->SPI_RDR;  //set the data
        // Serial.println(buf[header_length + row_shift + column_shift + k*TAXILES_PER_SLEEVE]);
        REG_PIOC_SODR = 1 << (ADC_SS_PIN_SHIFT_START + sleeve_ids[k]); //turn correct SS pin high (read SAM3X datasheet section 31)
      }
      TOGGLE_COUNT_PIN  //toggle the count pin to move to the next sensor (read SAM3X datasheet section 31)
      delayMicroseconds(1);
    }
  }
  
  SerialUSB.write((uint8_t*) buf, 2*message_length);  //write the entire data buffer to the USB port

  TOGGLE_CLEAR_PIN  //set the count to zero
}

void cs_update() {  //this is called if a change is detected in the switches
  update_cs = true; //set update_cs to true so the switches are checked in the next loop
}
