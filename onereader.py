import usb.core
from time import sleep
import RPi.GPIO as GPIO

servo = 8
led1 = 37
led2 = 35
led3 = 33
led4 = 31
led5 = 29

GPIO.setmode(GPIO.BOARD)
GPIO.setup(servo, GPIO.OUT)

GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(led3, GPIO.OUT)
GPIO.setup(led4, GPIO.OUT)
GPIO.setup(led5, GPIO.OUT)

p=GPIO.PWM(servo, 50) #50Hz frequency

dev=usb.core.find(idVendor=0x1949, idProduct=0x041b)

if dev is None:
    print('Device not found')
    exit()

ep=dev[0].interfaces()[0].endpoints()[0]
i=dev[0].interfaces()[0].bInterfaceNumber
dev.reset()

if dev.is_kernel_driver_active(i):
    dev.detach_kernel_driver(i)

dev.set_configuration()
eaddr=ep.bEndpointAddress

ack=False
data=None

p.start(2.5) # starting duty cycle (it set the servo to 0 degree)

def ledcontrol(state):
    GPIO.output(led1, state)
    GPIO.output(led2, state)
    GPIO.output(led3, state)
    GPIO.output(led4, state)
    GPIO.output(led5, state)

def setAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(servo, True)
    p.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(servo, False)
    p.ChangeDutyCycle(duty)


ledcontrol(GPIO.HIGH)
sleep(1)
ledcontrol(GPIO.LOW)

while True:
    try:
        if data==None and ack==True:
            ack=False
            print('Turn servo')
            ledcontrol(GPIO.HIGH)
            p.ChangeDutyCycle(7.5)  #use 5.5 to move almost 90 deg
            #setAngle(90)
            sleep(1)
            GPIO.output(led1, GPIO.LOW)
            sleep(1)
            GPIO.output(led2, GPIO.LOW)
            sleep(1)
            GPIO.output(led3, GPIO.LOW)
            sleep(1)
            GPIO.output(led4, GPIO.LOW)
            sleep(1)
            GPIO.output(led5, GPIO.LOW)
            sleep(1)
            p.ChangeDutyCycle(2.5)
            #setAngle(0)
        elif ack==False:
            GPIO.output(led3, GPIO.LOW)
            sleep(1)
            GPIO.output(led3, GPIO.HIGH)
            
        data=dev.read(eaddr, 8)
        if len(data)>0:
            ack=True
            print(data)
    except usb.core.USBError as e:
        data=None
        if e.args == ('Operation timed out',):
            continue
    except KeyboardInterrupt:
        break

p.stop()
GPIO.cleanup()
usb.util.release_interface(dev, i)
dev.attach_kernel_driver(i)
