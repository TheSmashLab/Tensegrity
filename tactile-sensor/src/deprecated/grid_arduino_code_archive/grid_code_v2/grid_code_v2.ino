// this program is the initial version for the new tactile sensor. 14 pins are powered while 6 pins are analog read pins 

int Apin[6] = {A2,A3,A4,A5,A6,A7};

String val;

unsigned long time1(0), time2(0), time_dif(0);

void setup()
{
  Serial.begin(57600);  
  
  //set and configure digital pins to outputs
  //digital pins 0 and 1 are used for serial communication, so use A0 and A1 for the first two digital outputs
  pinMode(A0,OUTPUT);
  pinMode(A1,OUTPUT);  
  pinMode(2,OUTPUT);
  pinMode(3,OUTPUT);
  pinMode(4,OUTPUT);
  pinMode(5,OUTPUT);
  pinMode(6,OUTPUT);
  pinMode(7,OUTPUT);
  pinMode(8,OUTPUT);
  pinMode(9,OUTPUT);
  pinMode(10,OUTPUT);
  pinMode(11,OUTPUT);
  pinMode(12,OUTPUT);
  pinMode(13,OUTPUT);
   
  //set and configure analog pins to inputs
  pinMode(A2,INPUT);
  pinMode(A3,INPUT);
  pinMode(A4,INPUT);
  pinMode(A5,INPUT);
  pinMode(A6,INPUT);
  pinMode(A7,INPUT);
  
}



void loop()
{    //Power Column 1, read from row j, and power down column 1
  
  
  // begin reading from row 1 column 1 and move through each column. Read from row 2 column 1 and read through each column...etc.
  for(int j = 0; j < 6; j++)
  {
    //print a row indicator to be used for keeping track of which rows are being read. 
    val += j;
    val += '\t';
    
    //Power Column 1, read from row j, and power down column 1   
    PORTC |=_BV(PORTC0);  
    val += analogRead(Apin[j]); 
    val += '\t';
    PORTC &= ~_BV(PORTC0);   
    
    //Power Column 2, read from row j, and power down column 2    
    PORTC |=_BV(PORTC1);    
    val += analogRead(Apin[j]); 
    val += '\t';
    PORTC &= ~_BV(PORTC1);

    //Power Column 3, read from row j, and power down column 3    
    PORTD |=_BV(PORTD2);    
    val += analogRead(Apin[j]); 
    val += '\t';
    PORTD &= ~_BV(PORTD2);

    //Power Column 4, read from row j, and power down column 4    
    PORTD |=_BV(PORTD3);    
    val += analogRead(Apin[j]); 
    val += '\t';    
    PORTD &= ~_BV(PORTD3);

    //Power Column 5, read from row j, and power down column 5    
    PORTD |=_BV(PORTD4);    
    val += analogRead(Apin[j]); 
    val += '\t';   
    PORTD &= ~_BV(PORTD4);

    //Power Column 6, read from row j, and power down column 6    
    PORTD |=_BV(PORTD5);    
    val += analogRead(Apin[j]); 
    val += '\t';   
    PORTD &= ~_BV(PORTD5);

    //Power Column 7, read from row j, and power down column 7    
    PORTD |=_BV(PORTD6);    
    val += analogRead(Apin[j]); 
    val += '\t';  
    PORTD &= ~_BV(PORTD6);

    //Power Column 8, read from row j, and power down column 8    
    PORTD |=_BV(PORTD7);    
    val += analogRead(Apin[j]); 
    val += '\t';   
    PORTD &= ~_BV(PORTD7);
    
    //Power Column 9, read from row j, and power down column 9    
    PORTB |=_BV(PORTB0);    
    val += analogRead(Apin[j]); 
    val += '\t';   
    PORTB &= ~_BV(PORTB0);
    
    //Power Column 10, read from row j, and power down column 10    
    PORTB |=_BV(PORTB1);    
    val += analogRead(Apin[j]); 
    val += '\t';    
    PORTB &= ~_BV(PORTB1);
    
    //Power Column 11, read from row j, and power down column 11    
    PORTB |=_BV(PORTB2);    
    val += analogRead(Apin[j]); 
    val += '\t';   
    PORTB &= ~_BV(PORTB2);    

    //Power Column 12, read from row j, and power down column 12        
    PORTB |=_BV(PORTB3);    
    val += analogRead(Apin[j]); 
    val += '\t';   
    PORTB &= ~_BV(PORTB3);

    //Power Column 13, read from row j, and power down column 13        
    PORTB |=_BV(PORTB4);      
    val += analogRead(Apin[j]);
    time1 = micros();    
    val += '\t';
    time2 = micros();    
    PORTB &= ~_BV(PORTB4);       

    //Power Column 14, read from row j, and power down column 14
    PORTB |=_BV(PORTB5);    
    val += analogRead(Apin[j]);    
    PORTB &= ~_BV(PORTB5);
    
    Serial.println(val);
    
    time_dif = time2-time1;
    
    Serial.println(time_dif);
    val = 0;
  }
 
}













