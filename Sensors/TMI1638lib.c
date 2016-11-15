/*
 * tm1638.c
 * bjab, march 2016
 * modified by Robin
 * demo program interfacing TM1638 from Arduino UNO (ATmga238P)
 * reusing :
 *   -http://blog.3d-logic.com/2015/01/10/using-a-tm1638-based-board-with-arduino/
 *   -https://android.googlesource.com/platform/external/arduino/+/jb-mr1-dev/hardware/arduino/cores/arduino
 *
 * to keep things simple, we'll ony use PORTB
 *
 * Vcc : +5V, GND : ground
 * DIO : data		(PD2)
 * CLK : clock		(PD3)
 * STB : strobe		(PD4)
 *
 * #include this file, then use TMI1638_setup and TMI1638_writeNumber
 *
 */


#include <avr/io.h>
#include <stdint.h>
#define F_CPU 16E6
#include <util/delay.h>


#define HIGH 0x1
#define LOW  0x0


const uint8_t data = 3;
const uint8_t clock = 4;
const uint8_t strobe = 5;


uint8_t counting(void); // need to put them in .h
uint8_t scroll(void);
uint8_t TMI1638_readButtons(void);


// read value from pin
int TMI1638_readFromPin(uint8_t pin)
{
    if (PINB & _BV(pin)) { // if pin set in port
        return HIGH;
    } else {
        return LOW;
    }
}


// write value to pin
void TMI1638_writeToPin(uint8_t pin, uint8_t val)
{
    if (val == LOW) {
        PORTB &= ~(_BV(pin)); // clear bit
    } else {
        PORTB |= _BV(pin); // set bit
    }
}


// shift out value to data
void TMI1638_shiftOut (uint8_t val)
{
    uint8_t i;
    for (i = 0; i < 8; i++)  {
        TMI1638_writeToPin(clock, LOW);   // bit valid on rising edge
        TMI1638_writeToPin(data, val & 1 ? HIGH : LOW); // lsb first
        val = val >> 1;
        TMI1638_writeToPin(clock, HIGH);
    }
}


// shift in value from data
uint8_t TMI1638_shiftIn(void)
{
    uint8_t value = 0;
    uint8_t i;


    DDRB &= ~(_BV(data)); // clear bit, direction = input
    
    for (i = 0; i < 8; ++i) {
        TMI1638_writeToPin(clock, LOW);   // bit valid on rising edge
        value = value | (TMI1638_readFromPin(data) << i); // lsb first
        TMI1638_writeToPin(clock, HIGH);
    }
    
    DDRB |= _BV(data); // set bit, direction = output
    
    return value;
}


void TMI1638_sendCommand(uint8_t value)
{
    TMI1638_writeToPin(strobe, LOW);
    TMI1638_shiftOut(value);
    TMI1638_writeToPin(strobe, HIGH);
}


void TMI1638_reset()
{
    // clear memory - all 16 addresses
    TMI1638_sendCommand(0x40); // set auto increment mode
    TMI1638_writeToPin(strobe, LOW);
    TMI1638_shiftOut(0xc0);   // set starting address to 0
    for(uint8_t i = 0; i < 16; i++)
    {
        TMI1638_shiftOut(0x00);
    }
    TMI1638_writeToPin(strobe, HIGH);
}


void TMI1638_setup()
{
     DDRB |= 0b00111000; // set port D as output


    TMI1638_sendCommand(0x89);  // activate and set brightness to medium
//  reset();
}

// write value to LED
void TMI1638_setLed(uint8_t value, uint8_t position)
{
    TMI1638_sendCommand(0x44); // write position to fixed address 1
    TMI1638_writeToPin(strobe, LOW);
    TMI1638_shiftOut(0xC1 + (position << 1));
    TMI1638_shiftOut(value);
    TMI1638_writeToPin(strobe, HIGH);
}

// read buttons
uint8_t TMI1638_readButtons(void)
{
    uint8_t buttons = 0;
    TMI1638_writeToPin(strobe, LOW);
    TMI1638_shiftOut(0x42); // key scan (read buttons)


    DDRB &= ~(_BV(data)); // clear bit, direction = input


    for (uint8_t i = 0; i < 4; i++)
    {
        uint8_t v = TMI1638_shiftIn() << i;
        buttons |= v;
    }

    DDRB |= _BV(data); // set bit, direction = output
    TMI1638_writeToPin(strobe, HIGH);
    return buttons;
}


void TMI1638_writeDigit(uint8_t position, uint8_t value)
{
	uint8_t digits[] = { 0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f };
	TMI1638_sendCommand(0x44);
	TMI1638_writeToPin(strobe, LOW);
	TMI1638_shiftOut(0xc0 + (position << 1));
	TMI1638_shiftOut(digits[value]);
	TMI1638_writeToPin(strobe, HIGH);
}


void TMI1638_writeNumber(unsigned long number)
{
	unsigned int i; // Used for for loop
	for (i = 0; i < 8 ; i++) {
		TMI1638_writeDigit(7 - i, number % 10);
		number /= 10;
	}
}