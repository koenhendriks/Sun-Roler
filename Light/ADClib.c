/*
 * This file is used to convert an Analog signal to a Digital value (0-1024)
 *
 * The pin used is PIN A0
 *
 */

#include <avr/io.h>
#include <stdint.h>
#include <avr/sfr_defs.h>

/*
* ADC Init
*
* This function initializes the ADC by enabling it,
* setting the reference to Vcc (5V) &
* setting the prescaler to 128
*/
void ADC_init()
{
	// ref=Vcc, left adjust the result (8 bit resolution),
	// select channel 0 (PC0 = input)
	//ADMUX = (1<<REFS0)|(1<<ADLAR);
	//ADMUX = (1<<ADLAR);
	ADMUX = (1<<REFS0);
	// enable the ADC & prescale = 128
	ADCSRA = (1<<ADEN)|(1<<ADPS2)|(1<<ADPS1)|(1<<ADPS0);
}/** ADC getValue** This function returns a 16-bit value between 0 and 1024 representing the voltage.* Multiply the value by 5 and divide the value by 1024 to get the Voltage.*/uint16_t ADC_getValue()
{
	ADCSRA |= (1<<ADSC); // start conversion
	loop_until_bit_is_clear(ADCSRA, ADSC);
	//uint16_t value = (ADCH << 8 ) | (ADCL & 0xff);
	//value = ( value << 8 ) || ADCL;
	return ADC; // 10-bit resolution
}