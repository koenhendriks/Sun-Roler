/*
 * made by Robin
 *
 * Input = PORTA PIN0
 *
 */

#include <avr/io.h>
#include <stdint.h>
#include <avr/sfr_defs.h>

void ADC_init()
{
	// ref=Vcc, left adjust the result (8 bit resolution),
	// select channel 0 (PC0 = input)
	//ADMUX = (1<<REFS0)|(1<<ADLAR);
	//ADMUX = (1<<ADLAR);
	ADMUX = (1<<REFS0);
	// enable the ADC & prescale = 128
	ADCSRA = (1<<ADEN)|(1<<ADPS2)|(1<<ADPS1)|(1<<ADPS0);
}// unsigned int ADC_getValue()
// {
// 	ADCSRA |= (1<<ADSC); // start conversion
// 	loop_until_bit_is_clear(ADCSRA, ADSC);
// 	return ADCH; // 8-bit resolution, left adjusted
uint16_t ADC_getValue()
{
	ADCSRA |= (1<<ADSC); // start conversion
	loop_until_bit_is_clear(ADCSRA, ADSC);
	//uint16_t value = (ADCH << 8 ) | (ADCL & 0xff);
	//value = ( value << 8 ) || ADCL;
	return ADC; // 10-bit resolution
}