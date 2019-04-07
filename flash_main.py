from utilities import *
from pyb import *
from cmemgr import Mapper

servo_tween = Tween(on_updated=Servo(1).angle)


@key_handler('Y6')
def key2():
    print('key2 pressed')
    servo_tween.set_target(-90, expected_duration=3000)
    pass


@key_handler('Y7')
def key3():
    print('key3 pressed')
    servo_tween.set_target(0, expected_duration=3000)
    pass


@key_handler('Y8')
def key4():
    print('key4 pressed ')
    servo_tween.set_target(90, expected_duration=3000)


Mapper.run(use_main_thread=True)

