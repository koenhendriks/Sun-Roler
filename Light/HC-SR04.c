/*
* This file is used to communicate with the HC-SR04
*/
#include <avr/io.h>
#include <stdlib.h>
#include <avr/sfr_defs.h>

/*
* HCSR04_init
*
* Used to intialize the UART communication
*/
void HCSR04_init()
{
	// Iets met timers en poorten ofzo
	DDRB |= (1<< (PORTD4))		// This port is used for Echo
	PORTD &= ~(1<<PORTD3);		// Set the trigger port to low
	
	// Hier moet de timer geinitialiseerd worden denk ik
	
}



uint8_t getDistance(){
	// De afstand teruggeven
	// Iets met tijd en 343 m/s
}