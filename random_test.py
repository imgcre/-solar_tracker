from pyb import *
from main import *
from display import *

def test1():
    adc_x5 = ADC(Pin('X5'))
    adc_x6 = ADC(Pin('X6'))
    adc_x7 = ADC(Pin('X7'))
    adc_x8 = ADC(Pin('X8'))
    # 步进电机测试 X2  X3
    # 舵机测试
    # 四路ADC测试
    i = -90
    dir_ = False
    while True:
        stepper.step()
        Servo(1).angle(i)
        if dir_:
            i -= 1
            if i <= -90:
                dir_ = False
        else:
            i += 1
            if i >= 90:
                dir_ = True
        print([adc_xx.read() for adc_xx in [adc_x5, adc_x6, adc_x7, adc_x8]])
        pyb.delay(100)
    pass


# Y9 SCL
# Y10 SDA

oled = OLED(I2C(2, mode=I2C.MASTER))

def test2():
    # OLED测试
    oled.init()
    while True:
        for y in range(64):
            for x in range(128):
                oled.draw_point(x, y, auto_submit=False)
        oled.submit()
        for y in range(64):
            for x in range(128):
                oled.draw_point(x, y, False, auto_submit=False)
        oled.submit()

    pass


if __name__ == '__main__':
    test2()
