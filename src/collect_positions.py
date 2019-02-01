from stageXY_control import*
import zpiezoPI as zpi

from ctypes import cdll
import numpy
from define_micro_path import*
import cv2
import time
from msvcrt import getch



size_of_region = 200 #um
step_size_z = 0.5







if __name__ == "__main__":
	axis = '3'
	verbose = 1

	pidll = cdll.LoadLibrary('c:/Users/immuser/Documents/E710_GCS_DLL/E7XX_GCS_DLL_x64.dll')
	ID = pidll.E7XX_ConnectRS232(5,57600)

	zpi.initiate_axis(pidll,ID, axis,verbose)
	zpi.turn_servo_on(pidll,ID,axis,verbose)

	zpi.move_piezo(pidll,ID,axis,10.,verbose)
	


	ms = MS2000(which_port='COM1', verbose=False)
	xyz = XYZStage(ms2000_obj=ms, axes=('X', 'y'),verbose=False)
	coords = []

	def  OnMouseOver(event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			print([(x, y)])
			
		return "break"

	
	
	while True:
		key = ord(getch())

		print(key)
		if key == 56:
			
			qp = zpi.query_position(pidll,ID,axis,False)
			zpi.move_piezo(pidll,ID,axis,qp + step_size_z,False)
			time.sleep(0.1)
			print('up',zpi.query_position(pidll,ID,axis,False))
		if key == 50:
			
			qp = zpi.query_position(pidll,ID,axis,False)
			zpi.move_piezo(pidll,ID,axis,qp - step_size_z,False)
			time.sleep(0.1)
			print('down',zpi.query_position(pidll,ID,axis,False))
		if key == 53:
			print('r')
			#name = input("Press enter to continue, or 'q' to finish and process inputs.")
			pos = xyz.get_position()
			zpi.check_for_errors(pidll,False)
			pos['z'] = zpi.query_position(pidll,ID,axis,False)
			
			print('position saved',pos['x'],pos['y'],pos['z'])
			coords.append([float(pos['x']),float(pos['y']), float(pos['z'])])
			
		if key ==  ord("q"):
				break
	coords.append(coords[0])

			#move_piezo(pidll,ID,axis,4.5,verbose)+++++++++
	np_coords = np.array(coords)
	
	xy_pts,z_pts = return_points(np_coords, size_of_region,step_size_z,False)
	
	with open('POS_FILE.txt', 'w') as the_file:
		
		for x,y,z in zip(xy_pts[:,0],xy_pts[:,1],z_pts):
			the_file.write(str(x)+'\t'+str(y)+'\t'+str(z)+'\n')

	the_file.close()
	plt.figure()
	plt.scatter(xy_pts[:,0],xy_pts[:,1],s=(z_pts)*size_of_region)
	plt.plot(xy_pts[:,0],xy_pts[:,1],'r-')
	plt.scatter(np_coords[:,0],np_coords[:,1],s=np_coords[:,2]*138.)

	#plt.xlim(-0.1,1.1)
	#plt.ylim(-0.1,1.1)
	plt.show()


	pidll.E7XX_CloseConnection(ID)