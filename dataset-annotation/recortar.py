import numpy as np
import cv2
import math 

quadrado1 = cv2.imread('1.jpeg',cv2.IMREAD_COLOR)
vetor1 = cv2.imread('t1.png',cv2.IMREAD_COLOR)


# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []

regioes = []
clone = quadrado1.copy()

anotado = False
def click_and_crop(event, x, y, flags, param):
	global refPt, cropping, quadrado1,anotado,clone
	
 
	if event == cv2.EVENT_LBUTTONDOWN:
		if anotado == True:
		  quadrado1 = clone.copy()
		  anotado = False
		  refPt=[]
		refPt.append((x, y))
		print(refPt)
		cv2.circle(quadrado1,(x, y), 5, (255,255,255), -1)


cv2.namedWindow("image")
cv2.startWindowThread()
cv2.setMouseCallback("image", click_and_crop)
 
cMassa = lado = -1
p1=[]
p2=[]
cv2.namedWindow("recorte")
cv2.startWindowThread()
new_image=[]
# keep looping until the 'q' key is pressed
while True:
	# display the image and wait for a keypress
	cv2.imshow("image", quadrado1)
	key = cv2.waitKey(1) & 0xFF
        
	if len(refPt) == 4:
		
		anotado = True
		   
		print(refPt)
		l1 =   math.sqrt(pow(refPt[0][0]-refPt[1][0],2) + pow(refPt[0][1]-refPt[1][1],2))  ## 0 e 1
		l2 =   math.sqrt(pow(refPt[0][0]-refPt[3][0],2) + pow(refPt[0][1]-refPt[3][1],2))  ## 0 e 3
		l3 =   math.sqrt(pow(refPt[1][0]-refPt[2][0],2) + pow(refPt[1][1]-refPt[2][1],2)) ## 1 e 2 
		l4 =   math.sqrt(pow(refPt[1][0]-refPt[3][0],2) + pow(refPt[1][1]-refPt[3][1],2)) ## 1 e 3 
		
		cMassa = ((refPt[0][0]+refPt[1][0]+refPt[2][0]+refPt[3][0])/4.0 , (refPt[0][1] +refPt[1][1]+refPt[2][1]+refPt[3][1])/4.0)
		lado = (l1+l2+l3+l4)/4
		
		p1 = (int(cMassa[0] - lado/2), int(cMassa[1] - lado/2))
		p2 = (int(cMassa[0] + lado/2), int(cMassa[1] + lado/2))
		
		new_image = quadrado1[p1[0]:p2[0],p1[1]:p2[1]]
		
		
		print("Centro de Massa : ", cMassa)
		print(l1,l2,l3,l4,"Lado:",lado)
		print(p1,p2)
		cv2.rectangle(quadrado1, p1, p2, (255,255,255), thickness=2, lineType=8, shift=0)
		refPt=[]
            
	if anotado==True:
	    cv2.imshow("image", new_image)
	    
	if key == ord("r"):
		quadrado1 = clone.copy()
		anotado = False
		refPt=[]
		
	if key == ord("o") and anotado == True:
		print(cMassa,lado)
		anotado = False
		regioes.append((p1,p2))
                
	
	if key == ord("c"):
		break
 

cv2.waitKey(1)
cv2.destroyAllWindows()
cv2.waitKey(1)

print("ok")