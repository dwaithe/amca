from control.stageXY_control import*
import control.zpiezoPIcall as zpi

from control.define_micro_path import*
from ctypes import cdll
import numpy
import cv2
import time
from getch import getch #import msvcrt on windows




output_pos_file = '../pos_files/POS_FILE.txt'
size_of_region = 327 #um 133 for 100x and 655 for 20x
step_size_z = 0.5 #um 
sarea_w = [3000.,0.,-3000.,0] #um 8000 for slide 3000 for low bead 1000 for high bead.
sarea_h = [0.,3000.,0.,-3000.] #um
sindex = 0
random_sampling = True
random_locations = 40 #How many positions to take from set if random.

#Initialize XY stage
ms = MS2000(which_port='/dev/ttyUSB0', verbose=False)
xyz = XYZStage(ms2000_obj=ms, axes=('X', 'y'),verbose=False)

coords =[]



if __name__ == "__main__":
	
	
	qp = zpi._send_command('zmove', str(50.0))['value']
	time.sleep(0.1)
	print('Moved the Z-piezo: ',qp)
	print('Please manually change the focus of microscope to that of the cells to center the Z-piezo of the microscope.')

	def  OnMouseOver(event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			print([(x, y)])
			
		return "break"

	while True:
		key = ord(getch())

		#print(key)
		if key == 56:
			qp = float(zpi._send_command('qpos', 0.0)['value'])
			qp = zpi._send_command('zmove', str(qp+ step_size_z))['value']
			time.sleep(0.1)
			print('moved up to: ',qp)
		if key == 50:
			sindex
			qp = float(zpi._send_command('qpos', '')['value'])
			qp = zpi._send_command('zmove', str(qp- step_size_z))['value']
			time.sleep(0.1)
			print('moved down to:',qp)
		if key == 53:
			print('position saved.')
			#name = input("Press enter to continue, or 'q' to finish and process inputs.")
			pos = xyz.get_position()
			pos['z'] =float(zpi._send_command('qpos', '')['value'])
			
			print('positions saved',pos['x'],pos['y'],pos['z'])
			coords.append([float(pos['x']),float(pos['y']), float(pos['z'])])
			xyz.move(x_um = coords[-1][0]+sarea_w[sindex], y_um = coords[-1][1]+sarea_h[sindex], blocking=False)
			sindex +=1
			
		print('')	
		if key ==  ord("q"):
				#zpi._send_command('close', '')
				break
	coords.append(coords[0])

			
	np_coords = np.array(coords)
	
	xy_pts,z_pts = return_points(np_coords, size_of_region,step_size_z,False)
	
	#random sampling.
	if random_sampling:
		locs = np.random.choice(xy_pts.shape[0],random_locations,replace=False)
		locs = np.sort(locs)
		xy_pts = xy_pts[locs,:]
		zp_ts = z_pts[locs]
	
	
	with open(output_pos_file, 'w') as the_file:
		
		for x,y,z in zip(xy_pts[:,0],xy_pts[:,1],z_pts):
			the_file.write(str(np.round(x,2))+'\t'+str(np.round(y,2))+'\t'+str(np.round(z,2))+'\n')
	print('File written (''), proceed to acquisition.')
	the_file.close()
	plt.figure()
	plt.scatter(xy_pts[:,0],xy_pts[:,1],marker='s')
	plt.scatter(xy_pts[0,0],xy_pts[0,1],c='g',marker='s')
	plt.plot(xy_pts[:,0],xy_pts[:,1],'r-')
	for x,y in zip(xy_pts[:,0],xy_pts[:,1]):
		rsz = size_of_region//2
		xrect = [x-rsz,x+rsz,x+rsz,x-rsz,x-rsz]
		yrect = [y-rsz, y-rsz, y+rsz, y+rsz,y-rsz]
		plt.plot(xrect,yrect,'b-')
	#plt.scatter(np_coords[:,0],np_coords[:,1],s=np_coords[:,2])
	plt.axis('equal')

	#plt.xlim(-0.1,1.1)
	#plt.ylim(-0.1,1.1)
	plt.show()


	
