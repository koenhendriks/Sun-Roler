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
}/** Uart_transmit_value** This function sends 5 frames. The first one for the identification of the sensor* And the 4 thereafter contain the data (32-bits)*/void uart_transmit_value(uint8_t identification, uint8_t state, uint32_t data){	uart_transmit(identification);	uart_transmit(state);
	// This is used to split the 32bit over 4 frames of 8. (8x4 is 32)
	uart_transmit((data & 0xff000000UL) >> 24);
	uart_transmit((data & 0x00ff0000UL) >> 16);
	uart_transmit((data & 0x0000ff00UL) >>  8);
	uart_transmit((data & 0x000000ffUL)      );}/** Uart_receive** This function returns the uart receive buffer. You can check if* there is data in this buffer by calling uart_check_receivebuffer()*/uint8_t uart_receive(){	return UDR0;	// Accessing UDR 0 should reset the RXC0 bit}/** Uart_check_receivebuffer** This function returns 1 when there is data in the receive buffer* This functions returns 0 when there isn't any data in the receive buffer** You can get the data out of the receive buffer by calling uart_receive()*/uint8_t uart_check_receivebuffer(){	if (bit_is_set(UCSR0A, RXC0) > 0){		return 1;	} else {		return 0;	}}