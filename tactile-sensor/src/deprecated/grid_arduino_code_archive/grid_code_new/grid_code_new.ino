// this program is the initial version for the new tactile sensor. 14 pins are powered while 6 pins are analog read pins

int Dpin[27]; 

char Apin[11] = {A5,A6,A7,A8,A9,A10,A11,A12,A13,A14,A15};

long t1, t2, t_dif;

void setup()
{
  Serial.begin(115200);  
  
  //set and configure digital pins to outputs
  //digital pins 0 and 1 are used for serial communication, so use A0 and A1 for the first two digital outputs
 for( int i = 0; i < 11; i++)
 {
   pinMode(Apin[i],INPUT);
 }
   
  for( int i = 0; i < 13; i++) 
  {
   Dpin[i] = i+37;
   pinMode(Dpin[i],OUTPUT);
  }
  
   for( int i = 13; i < 27; i++) 
  {
   Dpin[i] = i+9;
   pinMode(Dpin[i],OUTPUT);
  }

}

void loop()
{
  // begin reading from row 1 column 1 and move through each column. Read from row 2 column 1 and read through each column...etc.
  for(int j = 0; j < 11; j++)
  {
    //print a row indicator to be used for keeping track of which rows are being read. 
    Serial.print(j);
    Serial.print('\t');
    
    // cycle through each of the digital I/O pins
    for(int i = 0; i < 27; i++)
    {
     digitalWrite(Dpin[i],HIGH);
     //delay(1);
     int val = analogRead(Apin[j]); 
     //delay(1);
     t1 = micros();
     //Serial.print(val);
     
     TWCR = (1<<TWINT)|(1<<TWSTA)|(1<<TWEN);
     while(!(TWCR & (1<<TWINT)));
     if((TWSR & 0xF8) != 0x08)
     {Serial.print("error");}
     TWDR = 0b10000100;
     TWCR = (1<<TWINT) |(1<<TWEN);
     while(!(TWCR & (1<<TWINT)));
     if((TWSR & 0xF8) != 0b0)
     {Serial.print("error1");}
     TWDR = 0b10000011;//byte(val);
     TWCR = (1<<TWINT) | (1<<TWEN);    
     while(!(TWCR & (1<<TWINT)));

     if((TWSR & 0xF8) != 0x08)
     {Serial.print("error2");}

     TWCR = (1<<TWINT)|(1<<TWEN)|(1<<TWSTO);
     
     t2 = micros();
     t_dif = t2-t1;
     digitalWrite(Dpin[i],LOW);
     //delay(1);
     if(i < 26)
     {
       Serial.print("\t");
     }

    }
    
    Serial.println();
              Serial.println(t_dif);
  }
}



