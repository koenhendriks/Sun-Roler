/*
* This file is used to communicate with the HC-SR04
*/
#include <avr/io.h>
#include <stdlib.h>
#include <avr/sfr_defs.h>
#define F_CPU 16E6
#include <util/delay.h>

/*
* HCSR04_init
*
* Used to intialize the UART communication
*/
void HCSR04_init()
{
	DDRD &=~ (1 << PIND3);
	DDRD |= (1 << PIND2);
	
	TCCR1B |= (1 << CS10); //No prescaling
	TCNT1 = 0;			//Reset timer
	TIMSK1 |= (1 << TOIE1); //Timer overflow interrupt enable
	
	EICRA |= (1 << ISC10); //Any logical change on INT1
	EIMSK |= (1 << INT1); //Enable INT1
}

unsigned char working;
unsigned char rising_edge;

uint8_t error;

void Send_signal()
{
	if(working ==0) //Be sure that conversation is finished
	{
		_delay_ms(50);		//Restart HC-SR04
		PORTD &=~ (1 << PIND2);
		_delay_us(1);
		PORTD |= (1 << PIND2); //Send 10us second pulse
		_delay_us(10);
		PORTD &=~ (1 << PIND2);
		working = 1;	//Be sure that it is ready
		error = 0;		//Clean errors
	}
}