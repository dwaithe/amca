#!python3

# --------------------------------------------------------
# AMCA - Automated Microscope Control Algorithm
# by Dominic Waithe
# 
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""

#General imports.
import argparse
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import tifffile
import sys
import time

#darknet3AB import
sys.path.append("../../darknet3AB/darknet")
import darknet as dk
import darknet_video as dkv

#Stage control.
from control.stageXY_control import*
import control.zpiezoPIcall as zpi

#ROI library for tifffile to make ROI compatible with ImageJ

from ijroi.ij_roi import Roi
from ijroi.ijpython_encoder import encode_ij_roi, RGB_encoder

#Import camera libary.
from pyvcam import pvc
from pyvcam.camera import Camera







ms = MS2000(which_port='/dev/ttyUSB0', verbose=False)
xyz = XYZStage(ms2000_obj=ms, axes=('X', 'y'),verbose=False)


#plt.ion()
class DynamicUpdate():
	def __init__(self):

		self.img_stk = {}
		self.description = {}
		self.pos_x = []
		self.pos_y = []
		self.pos_z = []
		self.regions = {}
		
		

		self.pos_index = 0
		self.z_index = 1
		self.scanning_up = False
		self.scanning_down = False
		self.naive = True

		#Image limits for drawing.
		self.lim_min_x = 0
		self.lim_max_x = 512
		self.lim_min_y = 0
		self.lim_max_y =512
		self.z_stage_move = 0.5
		self.voxel_xy = 0.26 #um


		
		
		
	def load_positions(self,path):
		"""This will read the position file which should have been defined before this script.
		--------------
		inputs:
		path - path to file.
		outputs:
		None, but populates class pos_x ,pos_y, pos_z coordinate lists.		
		"""
		with open(path, 'r') as f:

			for line in f:
				items = line.split('\t')
				self.pos_x.append(float(items[0]))
				self.pos_y.append(float(items[1]))
				self.pos_z.append(float(items[2].split('\n')[0]))
		print('file positions loaded.')
	def init_output_positions(self,path):
		""" This will create the file which is the destination for the output coordinates.
		--------------
		inputs:
		path - path to file to be created for output positions.
		outputs:
		None, but creates file for output, assessible through instance of class.
		"""
		try:
			d.fout = open(path, "w")
		except: 
			#IOError
			pass
	

	def on_running(self,detections):
		sf = 3.4 #This is the ratio for correcting the visual output to the correct size.
		frame = np.zeros((int(self.lim_max_x),int(self.lim_max_y),3),np.uint8)
		key = cv2.waitKey(1)
		self.regions[self.stage_pos_z] = []
		
		d.detect_coords = []
		for detection in detections:
			x = (float(detection[2][0])/d.output_wid)*self.lim_max_x
			y = (float(detection[2][1])/d.output_wid)*self.lim_max_y
			w = (float(detection[2][2])/d.output_wid)*self.lim_max_x
			h = (float(detection[2][3])/d.output_wid)*self.lim_max_y
			xmin = int(round(x - (w / 2)))
			xmax = int(round(x + (w / 2)))
			ymin = int(round(y - (h / 2)))
			ymax = int(round(y + (h / 2)))
			score = detection[1]
			d.detect_coords.append([x,y,w,h,xmin,xmax,ymin,ymax,score])
			pt1 = (xmin, ymin)
			pt2 = (xmax, ymax)
			

			cv2.rectangle(frame, pt1,pt2, (0,255,0),1)
			self.regions[self.stage_pos_z].append([xmin,ymin,w,h])

				
			
			xoutpos = self.voxel_xy*xmin
			youtpos = self.voxel_xy*ymin
			woutpos = self.voxel_xy*h
			houtpos = self.voxel_xy*w
				
			d.fout.writelines(str(self.stage_pos_x)+","+str(self.stage_pos_y)+","+str(self.stage_pos_z)+","+str(xoutpos)+","+str(youtpos)+","+str(woutpos)+","+str(houtpos)+","+str(score)+"\n")			
			#Need both of these in order to rescale
		
		cv2.imshow('frame',frame)
		#k = cv2.waitKey(0)
		

	def on_move(self,stage_move_x,stage_move_y,stage_move_z):
		self.stage_pos_x = stage_move_x
		self.stage_pos_y = stage_move_y
		self.stage_pos_z = stage_move_z
		
		print('xyz',self.stage_pos_x,self.stage_pos_y,self.stage_pos_z)
		xyz.move(x_um = self.stage_pos_x, y_um = self.stage_pos_y, blocking=False)
		zpi._send_command('zmove',self.stage_pos_z)




def analyzeAndMove(detections):
	"""Detect object classes in an image using pre-computed object proposals."""
	
	###There has to be a bit of a delay to allow stage to catch up.
	delay = False
	
	# Detect all object classes and regress object bounds
	try:
		print("time:",time.time()-d.t1)
	except:
		pass
	
	d.t1 = time.time()
	
	
	intensity_score = []
	d.on_running(detections)

	if d.naive == True:
		if len(d.detect_coords) > 0:
			#This is the first time this image is seen and we have detected regions. 
			d.description[d.stage_pos_z] = []
			for detect in d.detect_coords:
				x,y,w,h,xmin,xmax,ymin,ymax,score = detect
				d.description[d.stage_pos_z].append(str(score)+','+str(xmin)+','+str(ymin)+','+str(w)+','+str(h))
			
			d.naive = False
			d.scanning_up = True
			d.scanning_down = False
			d.z_index = 1
		else:
			#This is the first time this image is seen but there are no regions detected. so we do nothing here and skip to next location
			d.pos_index += 1
			d.img_stk = {}
			d.description = {}
			pass

	else:
			
			if len(d.detect_coords) > 0:
				d.description[d.stage_pos_z] = []
				for detect in d.detect_coords:
					x,y,w,h,xmin,xmax,ymin,ymax,score = detect
					d.description[d.stage_pos_z].append(str(score)+','+str(xmin)+','+str(ymin)+','+str(w)+','+str(h))
			else:
				#If there are no more regions.
				if d.scanning_up == True and d.scanning_down == False:
					print('changeing direction.')
					d.scanning_down = True
					d.scanning_up = False
					d.z_index = 1
					delay = True
				
				elif d.scanning_up == False and d.scanning_down == True:
					## We have scanned up and down. No more cells. So we save and reset.
					d.scanning_down = False
					d.scanning_up = False
					d.naive = True
					d.z_index = 1
					d.pos_index += 1

					names = []
					for name in d.img_stk:
						names.append(float(name))
					names.sort()

					## Numpy stack of the correct size.
					np_stk = np.zeros((len(names),d.ch_to_save,d.lim_max_y,d.lim_max_x)).astype(np.float32)
					z = 0
					
					lets_get_meta = []
					for name in names:
						for ch in range(0,d.ch_to_save):
							np_stk[z,ch,:,:] = d.img_stk[name][ch].astype(np.uint16)
						regions = d.regions[name]
						
						z+=1
					
						for reg in regions:
							#print(reg[0],reg[1],reg[2],reg[3])
							r0 = np.clip(reg[0],0,d.lim_max_x)
							r1 = np.clip(reg[1],0,d.lim_max_y)
							r2 = np.clip(reg[2],0,d.lim_max_x)
							r3 = np.clip(reg[3],0,d.lim_max_y)
							roi_b = Roi(r0,r1,r2,r3, np_stk.shape[2],np_stk.shape[3],0)
							roi_b.name = "Region 1"
							roi_b.roiType = 1
							roi_b.setPositionH(1,z,-1)
							roi_b.strokeLineWidth = 1.0
							roi_b.strokeColor = RGB_encoder(255,255,0,0)
							lets_get_meta.append(encode_ij_roi(roi_b))

					
					metadata = {}
					metadata['hyperstack'] = True
					metadata['slices'] = np_stk.shape[0]
					metadata['channels'] =np_stk.shape[1]
					metadata['images'] = np.sum(np_stk.shape)
					metadata['ImageJ'] = '1.52g'
					metadata['Overlays']= lets_get_meta
					metadata['loop'] = False
					resolution = (d.voxel_xy/1000000.,d.voxel_xy/1000000.,'cm')
					out_file_path = d.out_path+"img_stk_x_"+str(d.stage_pos_x)+"y_"+str(d.stage_pos_y)+".tif"
					tifffile.imsave(out_file_path,np_stk,shape=np_stk.shape,resolution=resolution,imagej=True,ijmetadata=metadata)
					d.img_stk = {}
					d.regions = {}
				
	




	### What is the next movement to fulfill.
	if d.naive == True:
		d.on_move(d.pos_x[d.pos_index],d.pos_y[d.pos_index],d.pos_z[d.pos_index])
		time.sleep(1)
	if d.naive == False and d.scanning_up == True:

		move = d.z_stage_move * d.z_index
		d.on_move(d.pos_x[d.pos_index],d.pos_y[d.pos_index],d.pos_z[d.pos_index]+move)
		d.z_index += 1
	if d.naive == False and d.scanning_down == True:

		move = d.z_stage_move * d.z_index
		d.on_move(d.pos_x[d.pos_index],d.pos_y[d.pos_index],d.pos_z[d.pos_index]-move)
		d.z_index += 1
		if delay == True:
			time.sleep(1)
			delay = False
		
	return "session"





if __name__ == '__main__':

	print("Intializing data object")
	d = DynamicUpdate()
	
	print("initializing camera")
	
	pvc.init_pvcam()
	cam = [cam for cam in Camera.detect_camera()][0]
	cam.open()
	cam.gain = 1
	cam.binning = 2
	digital_binning = 2
	cam.exp_mode ="Timed"
	cam.exp_out_mode = 0
	###The number of channels to image.
	ch_to_image = 3 #Number of channels.
	exposures = [100, 300,300] ##Remember to coordinate with order in lamp.
	###The number of channels to analyze.
	ch_to_analyze = 1 ##Will always take first from available. Number not index.
	###The number of channels to save.
	ch_to_save = 3 ##Less than equal to ch_to_image, usually the same.
	
	d.ch_to_save = ch_to_save
	###Input and output.
	d.out_path = "/media/nvidia/UNTITLED/acquisitions/0001/"
	positions_file_path = "../pos_files/POS_FILE.txt"
	output_positions_file = "../pos_files/file_pos_export.txt"
	
	
	
	
	config_path = "../../darknet3AB/darknet/cfg/yolov2_dk3AB-classes-1-flip.cfg"
	meta_path =  "../../cell_datasets/c127_dapi_class/2018/obj_c127_dapi_class30.data"
	weight_path = "../../models/darknet/c127_dapi_class30/yolov2_dk3AB-classes-1-no-flip_final.weights" 
	
	###Loads and creates input and output files.
	d.load_positions(positions_file_path)
	d.init_output_positions(output_positions_file)
	### Loads the network in.
	netMain = dk.load_net_custom(config_path.encode("ascii"), weight_path.encode("ascii"), 0, 1)
	metaMain = dk.load_meta(meta_path.encode("ascii"))
	
	#Query postion of stage x and y.
	#d.pos = xyz.get_position()
	d.on_move(d.pos_x[0],d.pos_y[0],d.pos_z[0])
	
	###Just some tests before we engage.
	assert ch_to_image <= exposures.__len__(), "please define <= number of exposures as channels to image."
	
	
	#####The main loop. This will keep going till all the stage positions have been visited.
	while True:
		## Collect frame
		if ch_to_image >= 1:
			frame_CH1 = cam.get_frame(exp_time=exposures[0])[::2,::2]
			
		if ch_to_image >= 2:
			frame_CH2 = cam.get_frame(exp_time=exposures[1])[::2,::2]
		
		if ch_to_image >= 3:
			frame_CH3 = cam.get_frame(exp_time=exposures[2])[::2,::2]
			
		
		print(frame_CH1.shape)
		print("Running AMCA")
		
		if frame_CH1.shape[0] == 1024:
				im = np.zeros((1024,1024,3))
				
		elif frame_CH1.shape[0] == 512:
				im = np.zeros((512,512,3))
		else:
			print('unusual image shape',frame_CH1.shape[0])
			exit()
		
		print('recalculating')
		if ch_to_analyze == 1:
			frame_CH1_n = (frame_CH1/np.max(frame_CH1))*255.0		
			im[:,:,0] = frame_CH1_n
			im[:,:,1] = frame_CH1_n
			im[:,:,2] = frame_CH1_n
		
		elif ch_to_analyze == 2:
			frame_CH1_n = (frame_CH1/np.max(frame_CH1))*255.0
			frame_CH2_n = (frame_CH2/np.max(frame_CH2))*255.0
			im[:,:,0] =frame_CH1_n
			im[:,:,1] =frame_CH2_n	
		
		elif ch_to_analyze.__len__() == 3:
			frame_CH1_n = (frame_CH1/np.max(frame_CH1))*255.0
			frame_CH2_n = (frame_CH2/np.max(frame_CH2))*255.0
			frame_CH3_n = (frame_CH3/np.max(frame_CH3))*255.0
			im[:,:,0] =frame_CH1_n
			im[:,:,1] =frame_CH2_n
			im[:,:,2] =frame_CH3_n
			
		im = im.astype(np.uint8)
		d.output_wid = dk.network_width(netMain)
		
		darknet_image = dk.make_image(dk.network_width(netMain),dk.network_height(netMain),3)
		frame_resized = cv2.resize(im,(dk.network_width(netMain),dk.network_height(netMain)),interpolation=cv2.INTER_LINEAR)
		
		dk.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
		
		
		detections = dk.detect_image(netMain, metaMain, darknet_image, thresh=0.50)
		if len(detections) > 0:
			#Save image to stack.
			if ch_to_save == 1:
				d.img_stk[d.stage_pos_z] = frame_CH1
			if ch_to_save == 2:
				d.img_stk[d.stage_pos_z] = [frame_CH1,frame_CH2]
			if ch_to_save == 3:
				d.img_stk[d.stage_pos_z] = [frame_CH1,frame_CH2,frame_CH3]
		analyzeAndMove(detections)
		
	
	cam.close()
	pvc.uninit_pvcam()

			
