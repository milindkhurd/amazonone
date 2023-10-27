import usb.core
from time import sleep
import RPi.GPIO as GPIO

servo = 22
led1 = 11
led2 = 13
led3 = 15
led4 = 29
led5 = 31

GPIO.setmode(GPIO.BOARD)
GPIO.setup(servo, GPIO.OUT)
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(led3, GPIO.OUT)
GPIO.setup(led4, GPIO.OUT)
GPIO.setup(led5, GPIO.OUT)

p=GPIO.PWM(servo, 50) #50Hz frequency

##control = [5,5.5,6,6,5,7,7,5]

dev=usb.core.find(idVendor=0x1949, idProduct=0x041b)
if dev is None:
    print('Device not found')
    exit()

ep=dev[0].interfaces()[0].endpoints()[0]
i=dev[0].interfaces()[0].bInterfaceNumber
dev.reset()

if dev.is_kernel_driver_active(i):
    dev.detach_kernel_driver(i)

#usb.util.claim_interface(dev, i)
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

ledcontrol(GPIO.HIGH)
sleep(1)
ledcontrol(GPIO.LOW)

while True:
    try:
        if data==None and ack==True:
            ack=False
            print('Turn servo')
            ledcontrol(GPIO.HIGH)
            p.ChangeDutyCycle(7.5)
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
##            for x in range(6):
##                p.ChangeDutyCycle(control[x])
##                sleep(0.03)
##                print(x)
##            sleep(5)
##            for x in range(6, 0, -1):
##                p.ChangeDutyCycle(control[x])
##                sleep(0.03)
##                print(x)
##            p.ChangeDutyCycle(2.5)
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

GPIO.cleanup()
usb.util.release_interface(dev, i)
dev.attach_kernel_driver(i)
