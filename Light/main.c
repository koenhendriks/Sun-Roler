#include "AVR_TTC_scheduler.h"
#include "ADClib.c"
#include "UART.c"
#include "HC-SR04.c"
#include "TMI1638lib.c"
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sfr_defs.h>

void changeScreen(uint8_t change);

// The array of tasks
sTask SCH_tasks_G[SCH_MAX_TASKS];
/*------------------------------------------------------------------*-

  SCH_Dispatch_Tasks()

  This is the 'dispatcher' function.  When a task (function)
  is due to run, SCH_Dispatch_Tasks() will run it.
  This function must be called (repeatedly) from the main loop.

-*------------------------------------------------------------------*/

void SCH_Dispatch_Tasks(void)
{
   unsigned char Index;

   // Dispatches (runs) the next task (if one is ready)
   for(Index = 0; Index < SCH_MAX_TASKS; Index++)
   {
      if((SCH_tasks_G[Index].RunMe > 0) && (SCH_tasks_G[Index].pTask != 0))
      {
         (*SCH_tasks_G[Index].pTask)();  // Run the task
         SCH_tasks_G[Index].RunMe -= 1;   // Reset / reduce RunMe flag

         // Periodic tasks will automatically run again
         // - if this is a 'one shot' task, remove it from the array
         if(SCH_tasks_G[Index].Period == 0)
         {
            SCH_Delete_Task(Index);
         }
      }
   }
}

/*------------------------------------------------------------------*-

  SCH_Add_Task()

  Causes a task (function) to be executed at regular intervals 
  or after a user-defined delay

  pFunction - The name of the function which is to be scheduled.
              NOTE: All scheduled functions must be 'void, void' -
              that is, they must take no parameters, and have 
              a void return type. 
                   
  DELAY     - The interval (TICKS) before the task is first executed

  PERIOD    - If 'PERIOD' is 0, the function is only called once,
              at the time determined by 'DELAY'.  If PERIOD is non-zero,
              then the function is called repeatedly at an interval
              determined by the value of PERIOD (see below for examples
              which should help clarify this).


  RETURN VALUE:  

  Returns the position in the task array at which the task has been 
  added.  If the return value is SCH_MAX_TASKS then the task could 
  not be added to the array (there was insufficient space).  If the
  return value is < SCH_MAX_TASKS, then the task was added 
  successfully.  

  Note: this return value may be required, if a task is
  to be subsequently deleted - see SCH_Delete_Task().

  EXAMPLES:

  Task_ID = SCH_Add_Task(Do_X,1000,0);
  Causes the function Do_X() to be executed once after 1000 sch ticks.            

  Task_ID = SCH_Add_Task(Do_X,0,1000);
  Causes the function Do_X() to be executed regularly, every 1000 sch ticks.            

  Task_ID = SCH_Add_Task(Do_X,300,1000);
  Causes the function Do_X() to be executed regularly, every 1000 ticks.
  Task will be first executed at T = 300 ticks, then 1300, 2300, etc.            
 
-*------------------------------------------------------------------*/

unsigned char SCH_Add_Task(void (*pFunction)(), const unsigned int DELAY, const unsigned int PERIOD)
{
   unsigned char Index = 0;

   // First find a gap in the array (if there is one)
   while((SCH_tasks_G[Index].pTask != 0) && (Index < SCH_MAX_TASKS))
   {
      Index++;
   }

   // Have we reached the end of the list?   
   if(Index == SCH_MAX_TASKS)
   {
      // Task list is full, return an error code
      return SCH_MAX_TASKS;  
   }

   // If we're here, there is a space in the task array
   SCH_tasks_G[Index].pTask = pFunction;
   SCH_tasks_G[Index].Delay =DELAY;
   SCH_tasks_G[Index].Period = PERIOD;
   SCH_tasks_G[Index].RunMe = 0;

   // return position of task (to allow later deletion)
   return Index;
}

/*------------------------------------------------------------------*-

  SCH_Delete_Task()

  Removes a task from the scheduler.  Note that this does
  *not* delete the associated function from memory: 
  it simply means that it is no longer called by the scheduler. 
 
  TASK_INDEX - The task index.  Provided by SCH_Add_Task(). 

  RETURN VALUE:  RETURN_ERROR or RETURN_NORMAL

-*------------------------------------------------------------------*/

unsigned char SCH_Delete_Task(const unsigned char TASK_INDEX)
{
   // Return_code can be used for error reporting, NOT USED HERE THOUGH!
   unsigned char Return_code = 0;

   SCH_tasks_G[TASK_INDEX].pTask = 0;
   SCH_tasks_G[TASK_INDEX].Delay = 0;
   SCH_tasks_G[TASK_INDEX].Period = 0;
   SCH_tasks_G[TASK_INDEX].RunMe = 0;

   return Return_code;
}

/*------------------------------------------------------------------*-

  SCH_Init_T1()

  Scheduler initialisation function.  Prepares scheduler
  data structures and sets up timer interrupts at required rate.
  You must call this function before using the scheduler.  

-*------------------------------------------------------------------*/

void SCH_Init_T0(void)
{
   unsigned char i;

   for(i = 0; i < SCH_MAX_TASKS; i++)
   {
      SCH_Delete_Task(i);
   }

   // Set up Timer 0
   // Values for 1ms and 10ms ticks are provided for various crystals

   // Hier moet de timer periode worden aangepast ....!
   OCR0A = (uint8_t)250;   							// 1ms = (128/16.000.000) * 250
   TCCR0B = (1 << CS00) | (1 << CS01) | (1 << WGM02);	// prescale op 64, top counter = value OCR1A (CTC mode)
   TIMSK0 = 1 << OCIE0A;   								// Timer 1 Output Compare A Match Interrupt Enable
}

/*------------------------------------------------------------------*-

  SCH_Start()

  Starts the scheduler, by enabling interrupts.

  NOTE: Usually called after all regular tasks are added,
  to keep the tasks synchronized.

  NOTE: ONLY THE SCHEDULER INTERRUPT SHOULD BE ENABLED!!! 
 
-*------------------------------------------------------------------*/

void SCH_Start(void)
{
      sei();
}

/*------------------------------------------------------------------*-

  SCH_Update

  This is the scheduler ISR.  It is called at a rate 
  determined by the timer settings in SCH_Init_T1().

-*------------------------------------------------------------------*/

ISR(TIMER0_COMPA_vect)
{
   unsigned char Index;
   for(Index = 0; Index < SCH_MAX_TASKS; Index++)
   {
      // Check if there is a task at this location
      if(SCH_tasks_G[Index].pTask)
      {
         if(SCH_tasks_G[Index].Delay == 0)
         {
            // The task is due to run, Inc. the 'RunMe' flag
            SCH_tasks_G[Index].RunMe += 1;

            if(SCH_tasks_G[Index].Period)
            {
               // Schedule periodic tasks to run again
               SCH_tasks_G[Index].Delay = SCH_tasks_G[Index].Period;
               SCH_tasks_G[Index].Delay -= 1;
            }
         }
         else
         {
            // Not yet ready to run: just decrement the delay
            SCH_tasks_G[Index].Delay -= 1;
         }
      }
   }
}

// ------------------------------------------------------------------
// These values are used for the ultrasonic sensor
uint16_t timer_value = 0;
int distance_cm = 0;
// This value is used to store the amount of Lux
uint32_t totalLux= 0;
// These value are used to check if the sensor is connected to a central unit
uint8_t centralUnit_counter = 0;
char centralUnitConnected = 0;

// This is for Celcius
//uint8_t lowerLimit = 20;
//uint8_t upperLimit = 25;

// This is for Lux
uint16_t lowerLimit = 200;
uint16_t upperLimit = 300;


ISR (TIMER1_OVF_vect)
{
	if(rising_edge==1) //Check if there was echo
	{
		timer_value++;
		/*Check if isnt out of range*/
		if (timer_value > 91){
			working = 0;
			rising_edge = 0;
			error = 1;
		}
	}
}

ISR (INT1_vect)
{
	if(rising_edge==0){
		rising_edge=1;
		TCNT1 = 0;
		timer_value = 0;
	}
	else //Check if echo turned low, calculate distance
	{
		rising_edge = 0;
		distance_cm = TCNT1 / 1000;
	}
}

/*
* checkLux
*
* This function checks the amount of lux 25 times and stores the average
* in a value called 'totalLux'.
* This function is supposed to be called twice a minute (30s)
*/
void checkLux(){
	uint32_t lux = 0;
	for (uint8_t i = 0; i <= 25; i++){
		lux += getLux();
	}
	totalLux += (lux/25);
}

/*
* sendDataOrChangeScreen
*
* This function is used to send UART frames containing the identification number
* and the amount of Lux measured over 50 samples (25 per 30 seconds).
* Afterwards it resets 'totalLux'
*/
void sendDataOrChangeScreen(){
	if (centralUnitConnected){
		uart_transmit_value(10, (totalLux/2));
	} else {
		if (totalLux/2 > upperLimit)
		{
			changeScreen(30);
		} else if (totalLux/2 < lowerLimit)
		{
			changeScreen(10);
		}
	}
	totalLux = 0;
}

/*
*
*
*
*/
uint16_t getDistance(){
	uint32_t value= 0;
	for ( uint8_t i = 0; i <= 10; i++){
		Send_signal();
		while (working = 0) {
			_delay_us(10);
		}
		value += distance_cm;
	}
	return (uint16_t) value / 10;
}

/*
* setLED
*
* 0 = green
* 1 = red
*/
void setLED(uint8_t color){
	// Clear LEDs
	PORTB = PORTB & ~_BV(PINB0);
	PORTB = PORTB & ~_BV(PINB2);
	if (color == 0){ // Green
		// Set green LED
		PORTB = PORTB | _BV(PINB0);
		} else { // Red
		// Set red LED
		PORTB = PORTB | _BV(PINB2);
	}
}

/*
*
*
*/
void changeScreen(uint8_t change){
	if (change > getDistance()){
		setLED(1);
		while (change > getDistance()){
			PORTB = PORTB | _BV(PINB1);
			_delay_ms(250);
			PORTB = PORTB & ~_BV(PINB1);
			_delay_ms(250);
			TMI1638_writeNumber(getDistance());
		}
		return;
	} else if (change < getDistance()){
		setLED(0);
		while (change < getDistance()){
			PORTB = PORTB | _BV(PINB1);
			_delay_ms(250);
			PORTB = PORTB & ~_BV(PINB1);
			_delay_ms(250);
			TMI1638_writeNumber(getDistance());
					
		}
		return;
	} else {
		return;
	}
}

void checkData(){
	if (uart_check_receivebuffer() == 1){
		uint8_t frame = uart_receive();
		if (frame > 0){
			centralUnit_counter = 255;
			if (frame < 255){
				changeScreen(frame);
			}
		}
	}
}

/*
* initLED
*
* Used to initialize the LEDs which represent the motor
*/
void initLED(){
	DDRB |= 0b00000111;		// Set B0 - B2 to output to accommodate for three LEDs
	PORTB = _BV(PORTB0);	// Set B0 high; this is the starting position
}

void checkCentralUnit(){
	if (centralUnit_counter < 1){
		centralUnitConnected = 0;
	} else {
		centralUnitConnected = 1;
	}
	centralUnit_counter = centralUnit_counter - 1;
}


// This isn't needed probably
void printDistance(){
	TMI1638_writeNumber(getDistance());
}

int main()
{
 	ADC_init();
	uart_init();
	initLED();
	TMI1638_setup();
	TMI1638_writeNumber(10);
	HCSR04_init();
 	SCH_Init_T0();
	 
 	SCH_Add_Task(checkLux, 0, 30000);		// Check light levels; Every 30 seconds
 	SCH_Add_Task(checkData, 500, 5000);	// Check UART data; Every 5 seconds with a delay of 0,5 second
 	SCH_Add_Task(sendDataOrChangeScreen, 1000, 60000);	// Send data via UART; Every 60 seconds with a delay of 1 second
 	SCH_Add_Task(checkCentralUnit, 500, 1000);	// Send data via UART; Every second with a delay of 0,5 second
	SCH_Add_Task(printDistance, 0, 1000);
	
 	SCH_Start();
 	while(1){
 		SCH_Dispatch_Tasks();
 	}
	return(0);
}