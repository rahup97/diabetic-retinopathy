#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import math
from firebase import firebase

# use bcm gpio
GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

#set up initial firebase
myproj = firebase.FirebaseApplication('<link_to_firebase_instance>', None)

# Physical pins 11,15,16,18 for 1
# Gpio pins are 17, 22, 23, 24 for 1
# Physical pins 31, 33, 35, 37 for 2
# and gPIO is 6, 13, 19, 26 for 2
stepper1 = [17, 22, 23, 24]
stepper2 = [06, 13, 19, 26]

# for rotation
sequence = [[1, 0, 0, 1], [1, 0, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0],
            [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1]]
count = len(sequence)
delay = 10 / float(1000)

# make o/p


def initialise():
    GPIO.setup(12, GPIO.OUT)

    for x in stepper1:
        print "Setup pins"
        GPIO.setup(x, GPIO.OUT)
        GPIO.output(x, False)

    for x in stepper2:
        print "Setup pins"
        GPIO.setup(x, GPIO.OUT)
        GPIO.output(x, False)

    time.sleep(1)


def rotate1(steps, direct):
    s = 0
    i = 0
    while s < steps:

        for item in range(0, 4):
            xpin = stepper1[item]
            if sequence[i][item] != 0:
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)

        i += direct

        # if it ends, it means it must start again
        if (i >= count):
            i = 0
        if (i < 0):
            i = count + direct

        s = s + 1

        time.sleep(delay)


def rotate2(steps, direct):
    s = 0
    i = 0
    while s < steps:
        #print s

        for item in range(0, 4):
            xpin = stepper2[item]
            if sequence[i][item] != 0:
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)

        i += direct

        # if it ends, it means it must start again
        if (i >= count):
            i = 0
        if (i < 0):
            i = count + direct

        s = s + 1

        time.sleep(delay)


def angle_to_steps(angle):
    steps = angle / 0.088
    return int(steps)


def point_to_angle(x1, y1):
    '''
    assuming distance from eye to laser is 80mm,
    and size of pupil or final image is to be 60mm,
    the x-wise translation by angle will be got from tangent,
    convert x1 to some mm value out of 60mm based on value.
    '''

    x_pixels = 400
    y_pixels = 400
    pupil = 130
    laser2eye = 10.0

    x_f = (x1 * pupil) / x_pixels
    x_rad = math.atan(x_f / laser2eye)
    x_deg = int(abs(math.degrees(x_rad)))

    y_f = (y1 * pupil) / y_pixels
    y_rad = math.atan(y_f / laser2eye)
    y_deg = int(abs(math.degrees(y_rad)))

    return x_deg, y_deg


def main():
    initialise()

    while True:
        fired = myproj.get('/Coordinates/mary@gmail,com/Image/fire', None)
        if fired == 1:
            break


    detected = []
    size = myproj.get('/Coordinates/mary@gmail,com/Image/number', None) # number of points
    #obtain values for detected coordinates
    print(size)
    for i in range(size):
        xtemp = myproj.get('/Coordinates/mary@gmail,com/Image/Latitude/' + str(i), None)
        ytemp = myproj.get('/Coordinates/mary@gmail,com/Image/Longitude/' + str(i), None)
        detected.append([xtemp, ytemp])

    print(detected)
    time.sleep(3)

    for point in detected:
        x = point[0]
        y = point[1]
        if x > 0 and y > 0:
            direct_1 = 1
            direct_2 = -1
            print(str(x) + " " + str(y) + " " + " Quadrant: 1")
            x_ang, y_ang = point_to_angle(x, y)
            step1 = angle_to_steps(x_ang)
            step2 = angle_to_steps(y_ang)

            rotate1(step1, direct_1)
            time.sleep(2)
            rotate2(step2, direct_2)
            GPIO.output(12, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(12, GPIO.LOW)

            direct_1 = -1
            direct_2 = 1

            rotate2(step2, direct_2)
            time.sleep(2)
            rotate1(step1, direct_1)
            time.sleep(2)


        # call rotate function with y_deg and x_deg
        elif x < 0 and y > 0:
            direct_1 = 1
            direct_2 = 1
            print(str(x) + " " + str(y) + " " + " Quadrant: 2")
            x_ang, y_ang = point_to_angle(x, y)
            step1 = angle_to_steps(x_ang)
            step2 = angle_to_steps(y_ang)

            rotate1(step1, direct_1)
            time.sleep(2)
            rotate2(step2, direct_2)
            GPIO.output(12, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(12, GPIO.LOW)

            direct_1 = -1
            direct_2 = -1

            rotate2(step2, direct_2)
            time.sleep(2)
            rotate1(step1, direct_1)
            time.sleep(2)



        # call rotate function with y_deg and x_deg
        elif x > 0 and y < 0:
            direct_1 = -1
            direct_2 = -1
            print(str(x) + " " + str(y) + " " + "Quadrant: 4")
            x_ang, y_ang = point_to_angle(x, y)
            step1 = angle_to_steps(x_ang)
            step2 = angle_to_steps(y_ang)

            rotate1(step1, direct_1)
            time.sleep(2)
            rotate2(step2, direct_2)
            GPIO.output(12, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(12, GPIO.LOW)

            direct_1 = 1
            direct_2 = 1

            rotate2(step2, direct_2)
            time.sleep(2)
            rotate1(step1, direct_1)
            time.sleep(2)



        # call rotate function with y_deg and x_deg
        elif x < 0 and y < 0:
            direct_1 = -1
            direct_2 = 1
            print(str(x) + " " + str(y) + " " + " Quadrant: 3")
            x_ang, y_ang = point_to_angle(x, y)
            step1 = angle_to_steps(x_ang)
            step2 = angle_to_steps(y_ang)

            rotate1(step1, direct_1)
            time.sleep(2)
            rotate2(step2, direct_2)
            GPIO.output(12, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(12, GPIO.LOW)

            direct_1 = 1
            direct_2 = -1

            rotate2(step2, direct_2)
            time.sleep(2)
            rotate1(step1, direct_1)
            time.sleep(2)


            # call rotate function with y_deg and x_deg
        else:
            # don't move, just trigger the laser
            print("Only shoot")
            GPIO.output(12, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(12, GPIO.LOW)

        time.sleep(3)

    GPIO.cleanup()


if __name__ == '__main__':
    main()
