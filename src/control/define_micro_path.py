import time
import matplotlib.path as mpltPath
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import sys
from bisect import bisect_left
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

def return_points(np_coords, size_of_region,step_size_z,verbose=False):
	"""
	Returns sampling points between measured calibration points at regular intervals,
	interpolates z-pts between these points.

	Inputs:
	--------------------
	np_coords      - m calibration points on the slide selected by the user [(x0,y0,z0),(x1,y1,z1),...,(xm,ym,zm)].
	size_of_region - Size of imaging region, and/or gap between imaged regions.

	Outputs:
	--------------------
	xy_pts         - points [(x0,y0),(x1,y1),...,(xn,yn)] sampled on grid.
	z_pts          - interpolated z points for sampling at pts.


	"""

	xmin = np.min(np_coords[:,0])
	xmax = np.max(np_coords[:,0])
	ymin = np.min(np_coords[:,1])
	ymax = np.max(np_coords[:,1])
	zmin = np.min(np_coords[:,2])
	zmax = np.max(np_coords[:,2])
	
	if verbose == True:
		print('xmin',xmin,'xmax',xmax,'ymin',ymin,'ymax',ymax)
		print('np_coords',np_coords)
	x,y = np.meshgrid(np.arange(xmin,xmax,size_of_region),np.arange(ymin,ymax,size_of_region))
	path = mpltPath.Path(np_coords[:,0:2])

	zpoints = np.arange(zmin,zmax,step_size_z)
	
	points = np.array([x.reshape(-1),y.reshape(-1)]).T
	inside = path.contains_points(points).reshape(x.shape)
	
	xy_pts = np.array([x[inside].reshape(-1), y[inside].reshape(-1)]).T
	z_pts = griddata(np_coords[:,0:2], np_coords[:,2], xy_pts, method='linear')

	zpts_int =[]
	for zpt in z_pts:
		zpts_int.append(takeClosest(zpoints,zpt))
	if verbose == True:
		plt.imshow(x)
	
	return xy_pts, np.array(zpts_int)





if __name__ == "__main__":


	
	
	
	#define coordinates.
	#points to search.
	coords = []
	coords.append([0.00, 0.0, 1.0])
	coords.append([0.0, 0.5, 0.2])
	coords.append([0.00, 1.0, 0.6])
	coords.append([1.0, 1.0, 0.2])
	coords.append([0.5, 0.5, 0.2])
	coords.append([1.0, 0.0, 1.0])
	coords.append([0.0, 0.0, 1.0])


	np_coords = np.array(coords)
	size_of_region = 0.1
	step_size_z = 0.5
	xy_pts,z_pts = return_points(np_coords, size_of_region,step_size_z,True)
	for xypt, zpt in zip(xy_pts,z_pts):
		print("x",xypt,'zpt',zpt)
	plt.show()
	plt.figure()
	plt.plot(np_coords[:,0],np_coords[:,1])
	plt.scatter(xy_pts[:,0],xy_pts[:,1],s=(z_pts)*100)
	plt.plot(xy_pts[:,0],xy_pts[:,1],'r-')
	plt.scatter(np_coords[:,0],np_coords[:,1],s=np_coords[:,2]*100)

	#plt.xlim(-0.1,1.1)
	#plt.ylim(-0.1,1.1)
	plt.show()

