import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import transforms
import time
from stageXY_control import*
import zpiezoPI as zpi
import tifffile
import mpl_toolkits.axisartist.floating_axes as floating_axes
from ctypes import cdll
import numpy as np
import time as time
from bisect import bisect_left

import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import cv2




mpl.rcParams['toolbar'] = 'None'
def rtn_comp(ax, alt, aht, bx, blt, bht, cx, clt, cht):
	return (ax > alt ) & (ax < aht)	& (bx > blt ) & (bx < bht ) & (cx > clt ) & (cx < cht )


def takeClosest(myList, myNumber):
	"""
	Assumes myList is sorted. Returns closest value to myNumber.
	If two numbers are equally close, return the smallest number.
	"""
	pos = bisect_left(myList, myNumber)
	if pos == 0:
		return myList[0]
	if pos == len(myList):
		return myList[-1]
	before = myList[pos - 1]
	after = myList[pos]
	if after - myNumber < myNumber - before:
	   return after
	else:
	   return before


axis = '3'
verbose = 1
um_distxy = 150 #um
imgfldx =400
um_distz = 40

pidll = cdll.LoadLibrary('c:/Users/immuser/Documents/E710_GCS_DLL/E7XX_GCS_DLL_x64.dll')
ID = pidll.E7XX_ConnectRS232(5,57600)
zpi.initiate_axis(pidll,ID, axis,verbose)
zpi.turn_servo_on(pidll,ID,axis,verbose)
zpi.check_for_errors(pidll,verbose)
zpi.query_position(pidll,ID,axis,verbose)
img = plt.imread('C:/Users/immuser/Documents/Faster-RCNN-TensorFlow-Python3.5-master/calibration/calibration_MMStack_Pos0.ome.tif')
img = np.flipud(img)
ms = MS2000(which_port='COM1', verbose=False)
xyz = XYZStage(ms2000_obj=ms, axes=('X', 'y'),verbose=False)
plt.ioff()
#figure = plt.figure(figsize=(5,5))
figure, ax = plt.subplots()
figure.patch.set_facecolor('white')
#ax = plt.Axes(figure, [.1, .1, .25, .80])
#ax = plt.subplot(gs[220:700, 190:870])
#ax.axis('equal')
		#Autoscale on unknown axis and known lims on the other
#ax.set_autoscaley_on(True)
#ax.set_xlim(0, 4096)
#ax.set_ylim(0, 4096)
#Other stuff
currentAxis = plt.gca()
#ax.grid()
ax.set_axis_bgcolor("black")
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

#plt.autoscale(False)
#Populate acquisition stage positions dictionary for quick hash lookup.
fpos = open("POS_FILE.txt", "r")
lines = fpos.readlines()
pos_dic = {}
xps_arr = []
yps_arr = []
zps_arr = []
for line in lines:
#For this application the units are um and we round to the nearest um.
		pos = line.split('\n')[0].split('\t')
		xps = np.round(float(pos[0]),0)
		yps = np.round(float(pos[1]),0)
		zps = np.round(float(pos[2]),0)
		ref = str(xps)+'_'+str(yps)#+'_'+str(zps)
		pos_dic[ref] = [[xps,yps,zps],[]]
		xps_arr.append(xps)
		yps_arr.append(yps)
		zps_arr.append(zps)
xyz.move(x_um = xps_arr[0], y_um = yps_arr[0], blocking=True)
zpi.move_piezo(pidll,ID,axis,zps_arr[0],verbose)
xps_arr =  sorted(set(xps_arr))
yps_arr =  sorted(set(yps_arr))
zps_arr =  sorted(set(zps_arr))
print(xps_arr)
print(yps_arr)


#Populate list with all the detected squares.
fin = open("file_pos_export.txt", "r")
lines = fin.readlines()
regions =[]

for line in lines:
		region = line.split(',')
		#print('region',region.__len__())
		if region.__len__() == 7:
			xstg = float(region[0])
			ystg = float(region[1])
			xbox = float(region[3])
			ybox = float(region[4])
			xreg = float(region[0]) + float(region[3]) #This is the x position of square in world coordinates
			yreg = float(region[1]) + float(region[4]) #This is the y position of square in world coordinates
			zreg = float(region[2])
			wreg = float(region[5])
			hreg = float(region[6])
			regions.append([xstg,ystg,xreg,yreg,zreg,xbox,ybox,wreg,hreg])
		else:
			break
		

#Populate the dictionary with the detected squares closet to each region.
for ref1 in pos_dic:
	xps0,yps0,zps0 = pos_dic[ref1][0]
	for reg in regions:
		xstg,ystg,xreg,yreg,zreg,xbox,ybox,wreg,hreg = reg
		hit = rtn_comp(abs(xreg),abs(xps0)-um_distxy,abs(xps0)+um_distxy,yreg,yps0-um_distxy,yps0+um_distxy,zreg,zps0-um_distz,zps0+um_distz)
	
		if hit:
			add = True
			if add == True:
				pos_dic[ref1][1].append(reg) 

#a = return_ran(xregs_arr, pos['x'], pos['x']+(2048.*0.13))
#b = return_ran(yregs_arr, pos['y'], pos['y']+(2048.*0.13))
#c = return_ran(yregs_arr, pos['z']-25, pos['z']+25)
#print("b",xregs_arr.shape,b,b[0].shape)

regions = np.array(regions)
print('ref',ref)
for ref in pos_dic:
	print('ref',ref,pos_dic[ref][1].__len__())
	#print(pos_dic[ref],'\n')


posz= zpi.query_position(pidll,ID,axis,verbose=False)
pos = {}
#posz = 15.0222965208
#pos['x'] = -584.9
#pos['y'] = 364.7
c = 0

thismanager = plt.get_current_fig_manager()

plt.axis('equal')


plt.ylim()
#ax.set_position([0.0, 0, 1.0, 1.0], which='both')
#ax.imshow(img)
sxpos = 2129
sypos = 206
swpos = 593
shpos = 596
#(2171, 123, 332, 371)
thismanager.window.setGeometry(sxpos+8, sypos+31, swpos-16, shpos-39)
print(thismanager.window.frameGeometry())
#figure.show()

#plt.show()
#thismanager.window.setGeometry(2292, 152, 250, 334)
print(thismanager.window.frameGeometry())
def press(event):
	print('press', event.key)
	key = None

	print(event.key)
	if event.key == "8":
		
		qp = zpi.query_position(pidll,ID,axis,False)
		zpi.move_piezo(pidll,ID,axis,qp + 0.5,False)
		
		
	if event.key == "2":
		
		qp = zpi.query_position(pidll,ID,axis,False)
		zpi.move_piezo(pidll,ID,axis,qp - 0.5,False)
		pos['z'] = zpi.query_position(pidll,ID,axis,verbose=False)

sf =6.5
pos = xyz.get_position()
pos['z'] = zpi.query_position(pidll,ID,axis,verbose=False)

figure.canvas.mpl_connect('key_press_event', press)
figure.show()

print(zps_arr)
while True:
	

	t0 = time.time()
	#ax.clear()
	
	frame = np.zeros((int(2048/sf),int(2048/sf),3),np.uint8)
	
	key = cv2.waitKey(1)
	#if key == 27:
	#	break;
	#print(thismanager.window.frameGeometry())

	#print(thismanager.window.frameGeometry())
	#ax.set_position([0.75, 0.5, .40, 0.58], which='both')
	t1 = time.time()
	po = xyz.get_position()
	pos['x'] = po['x']
	pos['y'] = po['y']
	pos['z'] = zpi.query_position(pidll,ID,axis,verbose=False)
	#
	t2 = time.time()
	#print(pos['z'])
	ax.set_xlim([pos['x']+imgfldx, pos['x']-imgfldx])
	ax.set_ylim([(pos['y']+imgfldx),(pos['y']-imgfldx)])	
	
	valx = takeClosest(xps_arr, pos['x'])
	valy = takeClosest(yps_arr, pos['y'])
	#valz = takeClosest(zps_arr, pos['z']-4.)


	ref = str(valx)+'_'+str(valy)#+'_'+str(valz)
	#line, = ax.plot(np.random.randn(100))

	#print(thismanager.window.frameGeometry())
	try:
		print('ref',pos,ref,pos_dic[ref][1].__len__())
		for reg in pos_dic[ref][1]:
			xstg,ystg,xreg,yreg,zreg,xbox,ybox,wreg,hreg = reg
			
			
			if np.round(pos['z'],1)-0.1 <= np.round(zreg,1) and np.round(zreg,1) <= np.round(pos['z'],1)+0.1:
				
				xbox = (512-(xbox/0.13))*0.13
				

				xcoord = (xstg + xbox - wreg)-pos['x']
				ycoord = (ystg + ybox)-pos['y']

				cvx = int(512/sf)-int(((((xcoord/0.13))))/sf)
				cvy = int(512/sf)-int(((((ycoord/0.13))))/sf)+int(1024/sf)
				cvw = cvx+int(((wreg)/0.13)/sf)
				cvh = cvy+int(((hreg)/0.13)/sf)
				cv2.rectangle(frame, (cvx,cvy),(cvw,cvh), (255,0,0),1)
				
	except:
		print('fal',pos,ref)
		pass
#
	#print('limits',[pos['x']-imgfldx, pos['x']+imgfldx],[pos['y']-imgfldx, pos['y']+imgfldx])
	c +=1
	t3 = time.time()
	cv2.imshow('frame',frame)
	#figure.canvas.draw()
	#figure.canvas.flush_events()
	t4 = time.time()
	#print('time t4-t3',np.round(t4-t3,4),'t3-t2',np.round(t3-t2,4),'t2-t1',np.round(t2-t1,4),'t1-t0',np.round(t1-t0,4),np.round(1/(t4-t0),4)," fps")
	#time.sleep(0.01)
input("Press Enter to continue...")
#plt.plot([pos['x']-10,pos['x']+10,pos['x']+10,pos['x']-10,pos['x']-10],[pos['y']-10,pos['y']-10,pos['y']+10,pos['y']+10,pos['y']-10],'b-')
print(thismanager.window.frameGeometry())
input("Press Enter to continue...")