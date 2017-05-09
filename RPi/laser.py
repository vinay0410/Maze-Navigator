import numpy as np
import cv2
import time
import RPi.GPIO as GPIO
import socket 
import sys
from thread import *


red_lower = np.array([0, 0, 240])
red_upper = np.array([10, 10, 255])


def init():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(17, GPIO.OUT)
	GPIO.setup(18, GPIO.OUT)
	GPIO.setup(19, GPIO.OUT)
	GPIO.setup(13, GPIO.OUT)
	GPIO.setup(5, GPIO.OUT)
	GPIO.setup(6, GPIO.OUT)
	GPIO.setup(26, GPIO.OUT)
	
	GPIO.output(5, GPIO.HIGH)
	GPIO.output(6, GPIO.HIGH)
	GPIO.output(26, GPIO.HIGH)
	
	PWMR = GPIO.PWM(17, 60)
	PWMR1 = GPIO.PWM(18, 60)
	PWML = GPIO.PWM(19, 60)
	PWML1 = GPIO.PWM(13, 60)

	PWML.start(0)
	PWML1.start(0)
	PWMR.start(0)
	PWMR1.start(0)

def makesocket():
        host = ''
        port = 8888

        try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
                print "Socket Creation Failed"
                print "Error No " + msg[0] + "Error Message" + msg[1];
                sys.exit();
        print 'Socket created'

        try:
                sock.bind((host, port))
        except socket.error, msg:
                print "Bind Failed!. Error No. " + str(msg[0]) + " Error Message " + str(msg[1])
        	sys.exit()
	print "Bind Successful"
        sock.listen(10)

	print "Socket is now listening"
        return sock


def communicate(sock, reply):
	conn, addr = sock.accept()
	conn.send('Welcome to the server. Type something and hit enter\n')        
        print "Connected with addr: " + addr[0] + ":" + str(addr[1])
	while True:
	        data = conn.recv(1024)
    		var = json.loads(data)
		#reply = 'OK...' + data
		
    		conn.sendall(reply)
		if var["check"] == 1:
			print "Checkpoint Reached"
		elif var["move"] == 0:
			PWML.ChangeDutyCycle(0)
			PWML1.ChangeDutyCycle(0)
			PWMR.ChangeDutyCycle(0)
			PWMR1.ChangeDutyCycle(0)
			time.sleep(2)
		else:
			break	

	print "Check " + str(var["check"]) + "move " + str(var["move"])
	time.sleep(2)


def driveMotors(cx, cy, h, w):
	
	offset = 20.0
	
	motor = ( ( (h/2 - cy)/(h/2 - offset) )*100, ((h/2-cy)/(h/2-offset))*100)
	
	cx = ((cx-w/2)/(w/2 - offset))*100
	
	motor = (motor[0] + cx, motor[1] - cx)
	
	if (motor[0] < 0):
		if (motor[0] < 100):
			PWML.ChangeDutyCycle(100)
		else:
			PWML.ChangeDutyCycle(-motor[0])
		PWML1.ChangeDutyCycle(0)
	else:
		if (motor[0] > 100):
			PWML1.ChangeDutyCycle(100)
		else:
			PWML1.ChangeDutyCycle(motor[0])
		PWML.ChangeDutyCycle(0)
	
	if (motor[1] < 0):
		if (motor[1] < 100):
			PWMR.ChangeDutyCycle(100)	
		else:
			PWMR.ChangeDutyCycle(-motor[1])
		
		PWMR1.ChangeDutyCycle(0)
	else:
		PWMR.ChangeDutyCycle(0)
		if (motor[1]>100):
			PWMR1.ChangeDutyCycle(100)
		else:
			PWMR1.ChangeDutyCycle(motor[1])



def follow():

	cap = cv2.VideoCapture(0)
	
	while cv2.waitKey(1) != 27:
		ret, img = cap.read()
	    h, w = img.shape
		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		
	
		mask = cv2.inRange(hsv, red_lower, red_upper)
		contours,hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		
		
		cx = w/2
		cy = h/2
		if not contours:	
			communicate(sock, "Laser not visible")
			
		else:
			cnts = sorted(contours, key = cv2.contourArea, reverse = True)[:1]
			M = cv2.moments(np.array(cnts[0]))
			if M["m00"] != 0:
				cx = int(M['m10']/M['m00'])
				cy = int(M['m01']/M['m00'])
				cv2.circle(img, (cx, cy), 9, (0, 255, 0), -1)
				communicate(sock, "Following")
				driveMotors(cx, cy, h, w)
			else:
				communicate(sock, "Laser not visible")
				
	    #cv2.imshow("img", img)
				


sock = makesocket()
init()
follow()
	


