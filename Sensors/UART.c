/*
* This file is used to communicate via UART
*/
#include <avr/io.h>
#include <stdlib.h>
#include <avr/sfr_defs.h>

/*
* Uart_init
*
* Used to intialize the UART communication
*/
void uart_init()
{

	// disable U2X mode
	UCSR0A = 0;
	// enable transmitter and receiver
	UCSR0B = _BV(TXEN0) | _BV(RXEN0);
	// set the baudrate (19k2)
	UBRR0H = 0;
	UBRR0L = 51;
	// set frame format : asynchronous, 8 data bits, 1 stop bit, no parity
	UCSR0C = _BV(UCSZ01) | _BV(UCSZ00);
}

/*
* Uart_transmit
*
* This functions sends 8 bits of data (1 frame)
*/
void uart_transmit(uint8_t data)
{
	// wait for an empty transmit buffer
	// UDRE is set when the transmit buffer is empty
	loop_until_bit_is_set(UCSR0A, UDRE0);
	// send the data
	UDR0 = data;
}
	uart_transmit((data & 0x00ff0000UL) >> 16);
	uart_transmit((data & 0x0000ff00UL) >>  8);
	uart_transmit((data & 0x000000ffUL)      );