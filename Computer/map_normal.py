import cv2
import numpy as np
import math
import sys
import socket

#  Returns sine of an angle.
def sine(angle):
    return math.sin(math.radians(angle))

##  Returns cosine of an angle
def cosine(angle):
    return math.cos(math.radians(angle))

def readImageBinary(filePath):
    mazeImg = cv2.imread(filePath)
    grayImg = cv2.cvtColor(mazeImg, cv2.COLOR_BGR2GRAY)
    ret,binaryImage = cv2.threshold(grayImg,200,255,cv2.THRESH_BINARY)
    return binaryImage

def readImageHSV(filepath):
   img = cv2.imread(filepath)
   hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
   return hsv

def find_end_point(img):
	red_lower = np.array([0, 100, 100])
    	red_upper = np.array([20, 255, 255])	
	center = img[415:575, 415:575]
	mask = cv2.inRange(center, red_lower, red_upper)
	
	contours, heirarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	point = contours[0][0][0]	
	new = (point[0]-80, point[0]-80)
	a, b = cv2.cartToPolar(new[0], new[1])
        r = a[0]
	theta = (b[0]*180)/math.pi
	if (theta > 180):
        	theta = theta - 180
        else:
        	theta = theta + 180
        theta = int(theta/90) + 1
        print (1, theta)
	return (1, theta)


def convert_polar(img):
        img_blur = cv2.GaussianBlur(img, (3, 3), 0)
        ret, binary = cv2.threshold(img_blur, 200, 255, cv2.THRESH_BINARY)
        radius = 475
        mid = 495
        polar = np.zeros((radius, 360), np.uint8)
        polar = cv2.bitwise_not(polar)
        for theta in range(0, 360):
                sin = sine(-theta)
                cos = cosine(theta+180)
                for r in range(0, radius):
                        polar[r, theta] = binary[r*cos + mid, r*sin + mid]

        return polar


def findNeighbours(cell, level, cellnum):
	neigh = []	

	levels = [0, 4, 10, 15, 20]

	h, w = cell.shape
	#cv2.imwrite("cell.jpg", cell)
	for i in range(0, 5):
		if (cv2.countNonZero(cell[i:i+1]) < w/4):
			break
	if (i==4):
		lower = (((cellnum-1)*levels[level-1])/levels[level]) + 1
		higher = (((cellnum)*levels[level-1])/levels[level]) + 1
		print (level, cellnum)
		print (lower, higher)
		if lower==higher:
			neigh.append((level-1, lower))	
		else:	
			neigh.append((level-1, lower))
			neigh.append((level-1, higher))
	if (cellnum == 1 or cellnum == levels[level]):
		if (cellnum == 1):
			neigh.append((level, levels[level]))
			neigh.append((level, 2))
		else:
			neigh.append((level, 1))
			neigh.append((level, levels[level]-1))

	else:
		neigh.append((level, cellnum-1))
		neigh.append((level, cellnum+1))

	return neigh

def findMarkers(img):
	dictMarker = {}
	check = {}
	listOfMarkers = []
	levels = [0, 4, 10, 15, 20]
	params = cv2.SimpleBlobDetector_Params()
	params.filterByArea = True
	params.minArea = 250
	params.maxArea = 350
	detector = cv2.SimpleBlobDetector(params)
	keypoints = detector.detect(img)
	print "i'm here"
	for i in keypoints:
        	point = (i.pt[0] - 495, i.pt[1] - 495)
        	print point
		x, y = cv2.cartToPolar(point[1], point[0])
		print "polar"
		r = x[0]
        	theta = (y[0]*180)/math.pi
        	if (theta > 180):
                	theta = theta - 180
        	else:
                	theta = theta + 180
        	orig_theta = theta
		print (r, theta)
		r = int(r/98)
		theta = int(theta/(360/levels[r])) + 1
		print (r, theta)
		listOfMarkers.append((r, theta))
		check[(r, theta)] = (int(x[0]),int(orig_theta))
	#im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

	#cv2.imwrite("img.jpg", im_with_keypoints)
	markers = sorted(listOfMarkers, key=lambda x: x[0])
	i = 1
	print markers
	points = []
	for j in markers:
		if (j[0] == i):
			points.append(j)
		else:
			dictMarker[i] = points
			i = i+1
			points = []
			points.append(j)
			dictMarker[i] = points
	return dictMarker, check

def buildGraph(img):      ## You can pass your own arguments in this space.
        graph = {}
    ############################# Add your Code Here ################################
        max_levels = 4
        
	levels = [0, 4, 10, 15, 20]
        for level in range(1, max_levels+1):
                for cellnum in range(1, levels[level] + 1):
                        point = (level, cellnum)
        #               print point
			cell = img[((level-1)*98 + 78):(level*98 + 77) + 5, (cellnum-1)*(360/levels[level]):(cellnum)*(360/levels[level])]
                        neigh = findNeighbours(cell, level, cellnum)
                        graph[point] = neigh

	return graph

def findPath(graph, start, end, path=[]):           ## You can pass your own arguments in this space.
    ############################# Add your Code Here ################################
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
#           print 'somethings wrong'
            return None
        shortest = None
        for node in graph[start]:
            if node not in path:
                newpath = findPath(graph, node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath

	return shortest

def findOptimumPath(graph, start, end, list_of_markers, n):     ## You can pass your own arguments in this space.
        path_array = []
    #############  Add your Code here   ###############
        if not n:
                print 'im in'
#               print findPath(graph, start, end, path=[])
                return [findPath(graph, start, end, path=[])]
        if not graph.has_key(start):
                return None
        path_array = None
	
        for node in list_of_markers[n]:
                mp = findPath(graph, start, node, path=[])
		#del graph[start]
		dict2 = list_of_markers.copy()
		array = dict2[n][:]
		array.remove(node)
		dict2[n] = array
		if dict2[n]:
			print "inner"
			newpath = findOptimumPath(graph, node, end, dict2, n)
		else:
			print "outer"
			newpath = findOptimumPath(graph, node, end, list_of_markers, n-1)
        	print newpath
	        newpath.insert(0, mp)
		if newpath:
                        length = 0
                        length_s = 0
                        for i in range(0, len(newpath)):
                                length = length + len(newpath[i])
                        if path_array:
                                for i in range(0, len(path_array)):
                                        length_s = length_s + len(path_array[i])

                        if not path_array or length < length_s:
                                path_array = newpath
	return path_array

def convert2angle(arr):
	path = []
	height = 52
	levels = [0, 4, 10, 15, 20]
	for i in arr:
		temp = []
		print i
		for j in range(0, len(i)):
			print i[j]
			if j != (len(i) -1) and i[j+1][0] == (i[j][0] - 1):
				point = i[j]
				point = ((point[1]-1)*(360/levels[point[0]])+180/levels[point[0]],90- math.degrees(math.atan2((point[0]*25 + 12.5),height)))
			else:
				point = i[j]
				point = (int((point[1]-1)*(360/levels[point[0]])),90 - math.degrees(math.atan2((point[0]*25 + 12.5),height)))
		#	if (point[0] > 180):
		#		point = (point[0]- 180, 180 - point[1])
			point = (point[0],  int(point[1] - 90))
	#		point = (int(point[0]*10 + 600), int(point[1]*10 + 1500))
			temp.append(point)
		path.append(temp)
	return path

def orderList(check, shortest):
	orderedList = []
	for i in shortest:
		if i[0] == (4, 1):
			continue
		orderedList.append(check[i[0]])
	return orderedList

def createCheckPoints(checks):	
	myCheckpoints = []
	h = 52
	for i in checks:
		point = (i[1],90 - math.degrees(math.atan2(((i[0]*25)/98.0), h))) 
	#	if point[0] > 180:
	#		point = (point[0] - 180, 180 - point[1])
		point = (point[0],  int(point[1]- 90))
	#	point = (int(point[0]*10 + 600), int(point[1]*10 + 1500))
		myCheckpoints.append(point);

	return myCheckpoints

def main(filePath, flag = 0):
    img = readImageHSV(filePath)
    imgBinary = readImageBinary(filePath)
    
    #listofMarkers = findMarkers(img, size)
    #path = findOptimumPath(imgBinary, size, listofMarkers)
    #img = colourPath(imgBinary, path, size, 180)
    polar = convert_polar(imgBinary)
    graph = buildGraph(polar)
    print graph
    listOfMarkers, check = findMarkers(imgBinary)
    print listOfMarkers
    end = find_end_point(img)
    shortest = findOptimumPath(graph, (4, 1), end, listOfMarkers, 4)
    print shortest
    angles = convert2angle(shortest)
    print angles
    order = orderList(check, shortest)
    print order
    listOfChecks = createCheckPoints(order)
    print listOfChecks
    print check
    try:
    #create an AF_INET, STREAM socket (TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
        sys.exit();

    print 'Socket Created'

    host = '192.168.4.1'
    port = 8888


    s.connect((host , port))

    print 'Socket Connected to ' + host + ' on ip ' + host

    

    message = str(angles) + "\r"
    message1 = str(listOfChecks) + "\r"


    try :
    #Set the whole string
        s.sendall(message)
    except socket.error:
    #Send failed
       print 'Send failed'
       sys.exit()

    try :
    #Set the whole string
        s.sendall(message1)
    except socket.error:
    #Send failed
       print 'Send failed'
       sys.exit()


#Now receive data
    reply = s.recv(4096)

    print reply


    try :
    #Set the whole string
        s.sendall(message1)
    except socket.error:
    #Send failed
       print 'Send failed'
       sys.exit()


    reply = s.recv(4096)

    print reply

if __name__ == "__main__":
    filePath = "MAP.jpg"     ## File path for test image
    img = main(filePath)
    print sys.argv          ## Main function call
    """cv2.imshow("image",img)
    cv2.imwrite('image.jpg', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()"""
