
import cv2
import numpy as np
import subprocess
import os
import os.path

nameLog = "coordinates.log"
ImageDirectory = './logs-tito-1518737145/click_images/'
ImageOutput = ImageDirectory+"cordenadas/"


bashCommand = "cat ./logs-tito-1518737145/click_images/clickimagelogfile_tito.txt | cut -f8 -d'|' | tr  ' ' '\n' | sed '/^$/d' > "+nameLog+""

#cat /home/tito/Documents/pruebas/ResearchLogger/logs-tito-1518708401/click_images/clickimagelogfile_tito.txt | cut -f8 -d'|' | cut -f 1-2,5-6 -d',' | tr ' ' ',' > " +nameLog+ ""

p1 = subprocess.Popen(['bash','-c', bashCommand])
p1.wait()

if not os.path.exists(ImageOutput):
    os.makedirs(ImageOutput)

archivo = open(nameLog, "r")
for linea in archivo.readlines():
	#print linea
	X, Y, num, estado,imageName = linea.split(",")
	imageName = imageName.rstrip()
	#print X, Y
	#print num
	#print estado
	#print imageName
	#print ""
	#print ""+ImageDirectory+""+imageName+""
	path = os.path.join(ImageDirectory, imageName)
	if os.path.exists(path):
		pass
	else:
		print "no existe la imagen"

	img = cv2.imread(path)	
	
	if estado == "left_up" or estado == "right_up":
		imagen = cv2.circle(img,(int(X),int(Y)),1000,(255,0,0),-1)
		cv2.imwrite(""+ImageOutput+""+imageName+"",imagen)
		#print "izquierdo"
		
	if estado == "left_down" or estado == "right_down":
		imagen = cv2.circle(img,(int(X),int(Y)),75,(0,255,0),-1)
		cv2.imwrite(""+ImageOutput+""+imageName+"",imagen)
		#print "derecho"
	
	#imagen = cv2.circle(img,(int(X),int(Y)),10,(0,255,0),-1)

	cv2.imwrite(""+ImageOutput+""+imageName+"",imagen)
	#time.sleep(0.5)
	cv2.imshow("tito",imagen)
	wait=3000
	cv2.waitKey(wait)
	
cv2.destroyWindow('tito')
	

	#cv2.imwrite(""+ImageOutput+""+imageName+"",imagen)
	#cv2.imshow("img",imagen)

		
	#image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
	#cv2.imshow("image",img)

	#if int(X) != int(Xup):
	#	print "Se sospecha que se subraya algo"
	#else:
	#	"Click normal"
	#while(1):
#		cv2.imshow('image',img)
#		if cv2.waitKey(20) & 0xFF == 27:
#			break
