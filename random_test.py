from pyb import *

p = Pin('X1')  # X1 has TIM2, CH1
tim = Timer(2, freq=6400)
ch = tim.channel(1, Timer.PWM, pin=p)
ch.pulse_width_percent(50)
