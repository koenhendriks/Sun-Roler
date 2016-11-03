#include <avr/io.h>
#include <stdlib.h>
#include <avr/sfr_defs.h>
// output on USB = PD1 = board pin 1
// datasheet p.190; F_OSC = 16 MHz & baud rate = 19.200

void uart_init()
{
	// set the baud rate
	UBRR0H = 0;
	UBRR0L = 51;
	// disable U2X mode
	UCSR0A = 0;
	// enable transmitter
	UCSR0B = _BV(TXEN0);
	// set frame format : asynchronous, 8 data bits, 1 stop bit, no parity
	UCSR0C = _BV(UCSZ01) | _BV(UCSZ00);
}

void uart_transmit(uint8_t data)
{
	// wait for an empty transmit buffer
	// UDRE is set when the transmit buffer is empty
	loop_until_bit_is_set(UCSR0A, UDRE0);
	// send the data
	UDR0 = data;
}void uart_transmit_value(uint8_t identification, uint32_t data){	uart_transmit(identification);	uart_transmit((data & 0xff000000UL) >> 24);
	uart_transmit((data & 0x00ff0000UL) >> 16);
	uart_transmit((data & 0x0000ff00UL) >>  8);
	uart_transmit((data & 0x000000ffUL)      );}