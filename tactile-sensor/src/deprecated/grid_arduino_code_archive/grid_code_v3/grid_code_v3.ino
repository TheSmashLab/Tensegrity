// this program is the initial version for the new tactile sensor. 14 pins are powered while 6 pins are analog read pins 



String val;

unsigned long time1(0), time2(0), time_dif(0);

byte ADC_num[11] = {B100101, B100110, B100111, B100000, B100001, B100010, B100011, B100100, B100101, B100110, B100111};

void setup()
{
  Serial.begin(1000000);  
  
  //set and configure digital pins to outputs
  //digital pins 0 and 1 are used for serial communication, so use A0 and A1 for the first two digital outputs
  pinMode(22,OUTPUT);
  pinMode(23,OUTPUT);  
  pinMode(24,OUTPUT);
  pinMode(25,OUTPUT);
  pinMode(26,OUTPUT);
  pinMode(27,OUTPUT);
  pinMode(28,OUTPUT);
  pinMode(29,OUTPUT);
  pinMode(30,OUTPUT);
  pinMode(31,OUTPUT);
  pinMode(32,OUTPUT);
  pinMode(33,OUTPUT);
  pinMode(34,OUTPUT);
  pinMode(35,OUTPUT);
  pinMode(37,OUTPUT);
  pinMode(38,OUTPUT);
  pinMode(39,OUTPUT);
  pinMode(40,OUTPUT);
  pinMode(41,OUTPUT);
  pinMode(42,OUTPUT);
  pinMode(43,OUTPUT);
  pinMode(44,OUTPUT);
  pinMode(45,OUTPUT);
  pinMode(46,OUTPUT);
  pinMode(47,OUTPUT);
  pinMode(48,OUTPUT);
  pinMode(49,OUTPUT);

  //set and configure analog pins to inputs
  pinMode(A5,INPUT);
  pinMode(A6,INPUT);
  pinMode(A7,INPUT);
  pinMode(A8,INPUT);
  pinMode(A9,INPUT);
  pinMode(A10,INPUT);
  pinMode(A11,INPUT);
  pinMode(A12,INPUT);
  pinMode(A13,INPUT);
  pinMode(A14,INPUT);
  pinMode(A15,INPUT);
    
  //set ADCSARA Register in ATMega328
  ADCSRA = (1<<ADEN) | (1<<ADPS2);
}



void loop()
{    //Power Column 1, read from row j, and power down column 1
  time1 = micros();
  // begin reading from row 1 column 1 and move through each column. Read from row 2 column 1 and read through each column...etc.
  for(int j = 0; j < 6; j++)
  {
    
    //Set ADMUX Register in ATMega328 to the correspinding analog pin
    ADMUX = ADC_num[j];
    ADCSRB|=(1>>MUX5);
    //print a row indicator to be used for keeping track of which rows are being read. 
    val += j;
    val += '.';
    
    //Power Column 1, read from row j, and power down column 1   
    PORTC |=_BV(PORTC0);  
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTC &= ~_BV(PORTC0);   
    
    //Power Column 2, read from row j, and power down column 2    
    PORTC |=_BV(PORTC1);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTC &= ~_BV(PORTC1);

    //Power Column 3, read from row j, and power down column 3    
    PORTD |=_BV(PORTD2);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTD &= ~_BV(PORTD2);

    //Power Column 4, read from row j, and power down column 4    
    PORTD |=_BV(PORTD3);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';    
    PORTD &= ~_BV(PORTD3);

    //Power Column 5, read from row j, and power down column 5    
    PORTD |=_BV(PORTD4);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTD &= ~_BV(PORTD4);

    //Power Column 6, read from row j, and power down column 6    
    PORTD |=_BV(PORTD5);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTD &= ~_BV(PORTD5);

    //Power Column 7, read from row j, and power down column 7    
    PORTD |=_BV(PORTD6);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';  
    PORTD &= ~_BV(PORTD6);

    //Power Column 8, read from row j, and power down column 8    
    PORTD |=_BV(PORTD7);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTD &= ~_BV(PORTD7);
    
    //Power Column 9, read from row j, and power down column 9    
    PORTB |=_BV(PORTB0);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTB &= ~_BV(PORTB0);
    
    //Power Column 10, read from row j, and power down column 10    
    PORTB |=_BV(PORTB1);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';    
    PORTB &= ~_BV(PORTB1);
    
    //Power Column 11, read from row j, and power down column 11    
    PORTB |=_BV(PORTB2);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTB &= ~_BV(PORTB2);    

    //Power Column 12, read from row j, and power down column 12        
    PORTB |=_BV(PORTB3);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTB &= ~_BV(PORTB3);

    //Power Column 13, read from row j, and power down column 13        
    PORTB |=_BV(PORTB4);       
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTB &= ~_BV(PORTB4);       

    //Power Column 14, read from row j, and power down column 14
    PORTB |=_BV(PORTB5);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;    
    PORTB &= ~_BV(PORTB5);

    //Power Column 1, read from row j, and power down column 1   
    PORTC |=_BV(PORTC0);  
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTC &= ~_BV(PORTC0);   
    
    //Power Column 2, read from row j, and power down column 2    
    PORTC |=_BV(PORTC1);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTC &= ~_BV(PORTC1);

    //Power Column 3, read from row j, and power down column 3    
    PORTD |=_BV(PORTD2);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTD &= ~_BV(PORTD2);

    //Power Column 4, read from row j, and power down column 4    
    PORTD |=_BV(PORTD3);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';    
    PORTD &= ~_BV(PORTD3);

    //Power Column 5, read from row j, and power down column 5    
    PORTD |=_BV(PORTD4);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTD &= ~_BV(PORTD4);

    //Power Column 6, read from row j, and power down column 6    
    PORTD |=_BV(PORTD5);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTD &= ~_BV(PORTD5);

    //Power Column 7, read from row j, and power down column 7    
    PORTD |=_BV(PORTD6);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';  
    PORTD &= ~_BV(PORTD6);

    //Power Column 8, read from row j, and power down column 8    
    PORTD |=_BV(PORTD7);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTD &= ~_BV(PORTD7);
    
    //Power Column 9, read from row j, and power down column 9    
    PORTB |=_BV(PORTB0);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTB &= ~_BV(PORTB0);
    
    //Power Column 10, read from row j, and power down column 10    
    PORTB |=_BV(PORTB1);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';    
    PORTB &= ~_BV(PORTB1);
    
    //Power Column 11, read from row j, and power down column 11    
    PORTB |=_BV(PORTB2);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTB &= ~_BV(PORTB2);    

    //Power Column 12, read from row j, and power down column 12        
    PORTB |=_BV(PORTB3);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTB &= ~_BV(PORTB3);

    //Power Column 13, read from row j, and power down column 13        
    PORTB |=_BV(PORTB4);       
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTB &= ~_BV(PORTB4);     //Power Column 1, read from row j, and power down column 1   
    PORTC |=_BV(PORTC0);  
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTC &= ~_BV(PORTC0);   
    
    //Power Column 2, read from row j, and power down column 2    
    PORTC |=_BV(PORTC1);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTC &= ~_BV(PORTC1);

    //Power Column 3, read from row j, and power down column 3    
    PORTD |=_BV(PORTD2);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTD &= ~_BV(PORTD2);

    //Power Column 4, read from row j, and power down column 4    
    PORTD |=_BV(PORTD3);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';    
    PORTD &= ~_BV(PORTD3);

    //Power Column 5, read from row j, and power down column 5    
    PORTD |=_BV(PORTD4);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTD &= ~_BV(PORTD4);

    //Power Column 6, read from row j, and power down column 6    
    PORTD |=_BV(PORTD5);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTD &= ~_BV(PORTD5);

    //Power Column 7, read from row j, and power down column 7    
    PORTD |=_BV(PORTD6);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';  
    PORTD &= ~_BV(PORTD6);

    //Power Column 8, read from row j, and power down column 8    
    PORTD |=_BV(PORTD7);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTD &= ~_BV(PORTD7);
    
    //Power Column 9, read from row j, and power down column 9    
    PORTB |=_BV(PORTB0);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTB &= ~_BV(PORTB0);
    
    //Power Column 10, read from row j, and power down column 10    
    PORTB |=_BV(PORTB1);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';    
    PORTB &= ~_BV(PORTB1);
    
    //Power Column 11, read from row j, and power down column 11    
    PORTB |=_BV(PORTB2);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTB &= ~_BV(PORTB2);    

    //Power Column 12, read from row j, and power down column 12        
    PORTB |=_BV(PORTB3);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTB &= ~_BV(PORTB3);

    //Power Column 13, read from row j, and power down column 13        
    PORTB |=_BV(PORTB4);       
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTB &= ~_BV(PORTB4);     //Power Column 1, read from row j, and power down column 1   
    PORTC |=_BV(PORTC0);  
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTC &= ~_BV(PORTC0);   
    
    //Power Column 2, read from row j, and power down column 2    
    PORTC |=_BV(PORTC1);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTC &= ~_BV(PORTC1);

    //Power Column 3, read from row j, and power down column 3    
    PORTD |=_BV(PORTD2);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTD &= ~_BV(PORTD2);

    //Power Column 4, read from row j, and power down column 4    
    PORTD |=_BV(PORTD3);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';    
    PORTD &= ~_BV(PORTD3);

    //Power Column 5, read from row j, and power down column 5    
    PORTD |=_BV(PORTD4);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTD &= ~_BV(PORTD4);

    //Power Column 6, read from row j, and power down column 6    
    PORTD |=_BV(PORTD5);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTD &= ~_BV(PORTD5);

    //Power Column 7, read from row j, and power down column 7    
    PORTD |=_BV(PORTD6);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';  
    PORTD &= ~_BV(PORTD6);

    //Power Column 8, read from row j, and power down column 8    
    PORTD |=_BV(PORTD7);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTD &= ~_BV(PORTD7);
    
    //Power Column 9, read from row j, and power down column 9    
    PORTB |=_BV(PORTB0);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTB &= ~_BV(PORTB0);
    
    //Power Column 10, read from row j, and power down column 10    
    PORTB |=_BV(PORTB1);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';    
    PORTB &= ~_BV(PORTB1);
    
    //Power Column 11, read from row j, and power down column 11    
    PORTB |=_BV(PORTB2);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTB &= ~_BV(PORTB2);    

    //Power Column 12, read from row j, and power down column 12        
    PORTB |=_BV(PORTB3);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTB &= ~_BV(PORTB3);

    //Power Column 13, read from row j, and power down column 13        
    PORTB |=_BV(PORTB4);       
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTB &= ~_BV(PORTB4);     //Power Column 1, read from row j, and power down column 1   
    PORTC |=_BV(PORTC0);  
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTC &= ~_BV(PORTC0);   
    
    //Power Column 2, read from row j, and power down column 2    
    PORTC |=_BV(PORTC1);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTC &= ~_BV(PORTC1);

    //Power Column 3, read from row j, and power down column 3    
    PORTD |=_BV(PORTD2);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';
    PORTD &= ~_BV(PORTD2);

    //Power Column 4, read from row j, and power down column 4    
    PORTD |=_BV(PORTD3);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';    
    PORTD &= ~_BV(PORTD3);

    //Power Column 5, read from row j, and power down column 5    
    PORTD |=_BV(PORTD4);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTD &= ~_BV(PORTD4);

    //Power Column 6, read from row j, and power down column 6    
    PORTD |=_BV(PORTD5);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTD &= ~_BV(PORTD5);

    //Power Column 7, read from row j, and power down column 7    
    PORTD |=_BV(PORTD6);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';  
    PORTD &= ~_BV(PORTD6);

    //Power Column 8, read from row j, and power down column 8    
    PORTD |=_BV(PORTD7);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTD &= ~_BV(PORTD7);
    
    //Power Column 9, read from row j, and power down column 9    
    PORTB |=_BV(PORTB0);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTB &= ~_BV(PORTB0);
    
    //Power Column 10, read from row j, and power down column 10    
    PORTB |=_BV(PORTB1);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';    
    PORTB &= ~_BV(PORTB1);
    
    //Power Column 11, read from row j, and power down column 11    
    PORTB |=_BV(PORTB2);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTB &= ~_BV(PORTB2);    

    //Power Column 12, read from row j, and power down column 12        
    PORTB |=_BV(PORTB3);    
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC; 
    val += '.';   
    PORTB &= ~_BV(PORTB3);

    //Power Column 13, read from row j, and power down column 13        
    PORTB |=_BV(PORTB4);       
    // Start conversion by setting ADSC in ADCSRA Register
    ADCSRA |= (1<<ADSC);
    // wait until conversion complete ADSC=0 -> Complete
    while (ADCSRA & (1<<ADSC));
    // Get ADC the Result
    ADC = ADCH; 
    val += ADC;
    val += '.';   
    PORTB &= ~_BV(PORTB4); 
    
    Serial.println(val);
    val = 0;
  }
  time2 = micros(); 
  time_dif = time2-time1;
  //Serial.println(time_dif);
}













