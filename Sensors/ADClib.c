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

/*
* getLux
*
* This function is used to calculate the amount of Lux measured by the LDR
*/
double getLux(){
	double voltage = ADC_getValue() * 5;		// 5 is used because vcc = 5V.
	voltage = voltage / 1024;					/* 1024 is used because the ADC returns a value between
												   0 and 1024 representing the voltage. */
	float lux = (500*(5-voltage))/(10*voltage);	/* Lux is calculated by dividing 500 by the resistance of the LDR in kOhm
												   The resistance of the LDR is calculated by:
												   Vcc * R(light) = Vout * (R(light) + R(resistor)) 
												   Where
												   Vcc = 5V (Arduino)
												   Vout = the output of the circuit in Volt
												   R(light) = The resistance of the LDR
												   R(resistor) = 10 kOhm (The resistance of the resistor in the circuit in kOhm) */
	return lux;
}

/*
* getCeclius
*
* This function is used to calculate the amount of Celcius measured by the sensor
*/
double getCelcius(){
	double voltage = ADC_getValue() * 5;
	voltage = voltage / 1024;
	voltage -= 0.5;
	double temp = voltage * 100;
	return temp;
}