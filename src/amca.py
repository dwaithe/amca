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
import socket
import platform
import git

#For parsing the experimental configs, getting presets for each experiment.
from config_exp_parse import parse_acquisition_def

#darknet3AB import
sys.path.append("../../darknet3AB/darknet")
import darknet as dk
import darknet_video as dkv


#Stage control.
from control.stageXY_control import*
import control.zpiezoPIcall as zpi

#library for tifffile to make ROI compatible with ImageJ or OME
import save_img_out


#Import camera libary.
from pyvcam import pvc
from pyvcam.camera import Camera

#For focus prediction
from microscopeimagequality import prediction





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
		self.lower_focus_limit = 30 #um lower limit assuming initial is close to 50um
		self.upper_focus_limit = 70 #um upper limit assuming initial is close to 50um
		self.regions = {}
		self.scores = [] #for focusing.
		self.best_focus_idx = None
		self.best_focus = None
		self.focus_count = 10

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
		self.z_stage_move = None
		self.voxel_xy = None #um
	def init_camera(self):
		print("initializing camera")
	
		pvc.init_pvcam()
		self.cam = [cam for cam in Camera.detect_camera()][0]
		self.cam.open()
		self.cam.gain = self.cam_gain
		self.cam.binning = self.cam_binning
		self.cam.exp_mode ="Timed"
		self.cam.exp_out_mode = 0
	def cam_aquire(self,exposure,channel):
		return self.cam.get_frame(exp_time=exposure)

		
		
		
	def load_positions(self,positions_file_path):
		"""This will read the position file which should have been defined before this script.
		--------------
		inputs:
		path - path to file.
		outputs:
		None, but populates class pos_x ,pos_y, pos_z coordinate lists.		
		"""
		with open(positions_file_path, 'r') as f:

			for line in f:
				items = line.split('\t')
				self.pos_x.append(float(items[0]))
				self.pos_y.append(float(items[1]))
				self.pos_z.append(float(items[2].split('\n')[0]))
		print('file positions loaded.')
	def init_output_positions(self):
		""" This will create the file which is the destination for the output coordinates.
		--------------
		inputs:
		path - path to file to be created for output positions.
		outputs:
		None, but creates file for output, assessible through instance of class.
		"""
		try:
			d.fout = open(self.output_positions_file, "w")
		except: 
			IOError
			pass
	

	def on_running(self,detections):
		
		if self.display_out: 
			sf = 3.4 #This is the ratio for correcting the visual output to the correct size.
			frame = np.zeros((int(self.lim_max_x),int(self.lim_max_y),3),np.uint8)
			key = cv2.waitKey(1)
		self.regions[self.stage_pos_z] = []
		
		d.detect_coords = []
		for detection in detections:
			if self.analysis_method == 'object':
				x = (float(detection[2][0])/d.output_wid)*self.lim_max_x
				y = (float(detection[2][1])/d.output_hei)*self.lim_max_y
				w = (float(detection[2][2])/d.output_wid)*self.lim_max_x
				h = (float(detection[2][3])/d.output_hei)*self.lim_max_y
			elif(self.analysis_method == 'Crop'):
				x = self.clim_min_x + (float(detection[2][0])/d.output_wid)*(self.clim_max_x-self.clim_min_x)
				y = self.clim_min_y + (float(detection[2][1])/d.output_hei)*(self.clim_max_y-self.clim_min_y)
				w = (float(detection[2][2])/d.output_wid)*(self.clim_max_x-self.clim_min_x)
				h = (float(detection[2][3])/d.output_hei)*(self.clim_max_y-self.clim_min_y)
			xmin = int(round(x - (w / 2)))
			xmax = int(round(x + (w / 2)))
			ymin = int(round(y - (h / 2)))
			ymax = int(round(y + (h / 2)))
			score = detection[1]
			d.detect_coords.append([x,y,w,h,xmin,xmax,ymin,ymax,score])
			pt1 = (xmin, ymin)
			pt2 = (xmax, ymax)
			
			if self.display_out: cv2.rectangle(frame, pt1,pt2, (0,255,0),1)
			
			self.regions[self.stage_pos_z].append([xmin,ymin,w,h,score])

			xoutpos = self.voxel_xy*xmin
			youtpos = self.voxel_xy*ymin
			woutpos = self.voxel_xy*h
			houtpos = self.voxel_xy*w
				
			d.fout.writelines(str(self.stage_pos_x)+","+str(self.stage_pos_y)+","+str(self.stage_pos_z)+","+str(xoutpos)+","+str(youtpos)+","+str(woutpos)+","+str(houtpos)+","+str(score)+"\n")			
			#Need both of these in order to rescale
		
		if self.display_out:  cv2.imshow('frame',frame)
		
		

	def on_move(self,stage_move_x,stage_move_y,stage_move_z):
		self.stage_pos_x = np.round(stage_move_x,2)
		self.stage_pos_y = np.round(stage_move_y,2)
		self.stage_pos_z = np.round(stage_move_z,2)
		
		print('Moving Microscope to position (um): ',self.stage_pos_x,self.stage_pos_y,self.stage_pos_z)
		xyz.move(x_um = self.stage_pos_x, y_um = self.stage_pos_y, blocking=False)
		zpi._send_command('zmove_only',self.stage_pos_z)

def imageOnlyAndMove():

	
	d.pos_index += 1				
	lets_get_meta = []
	_zpos = []
	for z in d.img_stk:
		_zpos.append(float(z))
	_zpos.sort()
	
	## Numpy stack of the correct size.
	np_stk = np.zeros((1,len(_zpos),d.ch_to_save,d.lim_max_y,d.lim_max_x)).astype(d.exp_depth)
	z = 0				
			
	
	print('len',_zpos)
	z =0
	for zp in _zpos:
		for ch in range(0,d.ch_to_save):
			np_stk[0,z,ch,:,:] = d.img_stk[zp][ch].astype(d.exp_depth)
			
		z +=1
	
	if d.save_out == "ij_tiff":
		save_img_out.saveas_imagej_tiff(np_stk, [],d)
	elif d.save_out == "ome_tiff":
		save_img_out.saveas_ome_tiff(np_stk, [],d)
			
	d.img_stk = {}
	
	if d.pos_x.__len__() == d.pos_index:
		#We are at the end of list.
		return False 
		
	### What is the next movement to fulfill.	
	d.on_move(d.pos_x[d.pos_index],d.pos_y[d.pos_index],d.pos_z[d.pos_index])
	time.sleep(1)
	
		
	return True
def focusAndMove(score):
	"""Will measure focus score in each position, and control up/down direction. Finally, saves best focus position"""
	
	delay = False
	
	if d.naive == True:
		#This is the first time this image is seen and we have detected regions. 
		d.naive = False
		d.scanning_up = True
		d.scanning_down = False
		d.count = 0
		d.z_index = 1
		d.scores.append(score)
	else:
		current_min = np.min(d.scores)
		print('score',score,current_min)
		if d.scanning_up == True and d.scanning_down == False:
			d.scores.append(score)
			
		elif d.scanning_up == False and d.scanning_down == True:
			d.scores.insert(0,score)
		
		if d.count < d.focus_count:
			#This means that we have found a new minima and should keep searching.
			print('score and min',score,current_min)
			d.count += 1
			pass
			
		else:	
			
			if d.scanning_up == True and d.scanning_down == False:
				print('Changing direction.')
				d.scanning_down = True
				d.scanning_up = False
				d.z_index = 1
				delay = True
				d.count = 0
			elif d.scanning_up == False and d.scanning_down == True:
				## We have scanned up and down. No more cells. So we save and reset.
				d.scanning_down = False
				d.scanning_up = False
				d.naive = True
				d.z_index = 1
				

				d.names = []
				for name in d.img_stk:
					d.names.append(float(name))
				names_ordered = d.names
				names_ordered.sort()
				d.best_focus_idx = np.argmin(d.scores)
				d.best_focus = names_ordered[d.best_focus_idx]
				
			
				## Numpy stack of the correct size.
				np_stk = np.zeros((1,len(names_ordered),d.ch_to_save,d.lim_max_y,d.lim_max_x)).astype(d.exp_depth)
				z = 0
						
				lets_get_meta = []
				stack_rois = []
				for name in names_ordered:
					for ch in range(0,d.ch_to_save):
						np_stk[0,z,ch,:,:] = d.img_stk[name][ch].astype(d.exp_depth)
					#stack_rois.append([d.regions[name],z])
							
					z+=1
				###This is where we update the focus.
				if d.best_focus < d.lower_focus_limit or d.best_focus > d.upper_focus_limit:
					print('The best focus, for this section is at the limit. No permitting to go further. z-pos:',d.best_focus,' um')
				else:
					d.pos_z[d.pos_index] = d.best_focus
				
				
				
					
				print('write file')
				d.pos_index += 1
				if d.save_out == "ij_tiff":
					save_img_out.saveas_imagej_tiff(np_stk, stack_rois,d)
				elif d.save_out == "ome_tiff":
					save_img_out.saveas_ome_tiff(np_stk, stack_rois,d)
				d.best_focus_idx = None
				d.best_focus = None
				d.img_stk = {}
				d.scores = []		
	if d.pos_x.__len__() == d.pos_index:
		#We are at the end of list.
		return False 
	### What is the next movement to fulfill.
	if d.naive == True:
		d.on_move(d.pos_x[d.pos_index],d.pos_y[d.pos_index],d.pos_z[d.pos_index])
		time.sleep(3)
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
		
	return True
	


def analyzeAndMove(detections):
	"""Detect object classes in an image using pre-computed object proposals."""
	
	###There has to be a bit of a delay to allow stage to catch up.
	delay = False
	
	# Detect all object classes and regress object bounds
		
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
					print('Changing direction.')
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
					np_stk = np.zeros((1,len(names),d.ch_to_save,d.lim_max_y,d.lim_max_x)).astype(d.exp_depth)
					z = 0
					
					lets_get_meta = []
					stack_rois = []
					for name in names:
						for ch in range(0,d.ch_to_save):
							np_stk[0,z,ch,:,:] = d.img_stk[name][ch].astype(d.exp_depth)
						stack_rois.append([d.regions[name],z])
						
						z+=1
					
						

					if d.save_out == "ij_tiff":
						save_img_out.saveas_imagej_tiff(np_stk, stack_rois,d)
					elif d.save_out == "ome_tiff":
						save_img_out.saveas_ome_tiff(np_stk, stack_rois,d)
					
					d.img_stk = {}
					d.regions = {}
				
	



	if d.pos_x.__len__() == d.pos_index:
		#We are at the end of list.
		return False 
	### What is the next movement to fulfill.
	if d.naive == True:
		d.on_move(d.pos_x[d.pos_index],d.pos_y[d.pos_index],d.pos_z[d.pos_index])
		time.sleep(3)
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
		
	return True




if __name__ == '__main__':
	parser = argparse.ArgumentParser()
   
	parser.add_argument('--exp', required=True)
	

	args = parser.parse_args()
	

	params = parse_acquisition_def(args.exp)
	print("Intializing data object")
	d = DynamicUpdate()
	d.amcarepo = git.Repo("../").head.object.hexsha
	
	###The number of channels to image.
	d.ch_to_image = params['ch_to_image'] #Number of channels.
	d.excitation_lines = params['excitation_lines']#['1V','3GYR']#['1V','2B','3GYR']
	d.exposures = params['exposures']#[50, 300] ##Remember to coordinate with order in lamp.
	###The number of channels to analyze.
	d.ch_to_analyze = params['ch_to_analyze']#1 ##Will always take first from available. Number not index.
	###The number of channels to save.
	d.ch_to_save = params['ch_to_save']#2 ##Less than equal to ch_to_image, usually the same.
	d.cam_gain = params['cam_gain']#1 ##Camera gain.
	d.cam_binning = params['cam_binning']#2 #Binning to set camera to collect at
	d.lim_min_x = params['lim_min_x']#0 #expected limits. Should correspond with what is coming out of camera.
	d.lim_max_x = params['lim_max_x']#512 #expected limits
	d.lim_min_y = params['lim_min_y']#0 #expected limits
	d.lim_max_y = params['lim_max_y']#512 #expected limits
	d.clim_min_x = params['clim_min_x']#0 #expected limits. Should correspond with what is coming out of camera.
	d.clim_max_x = params['clim_max_x']#512 #expected limits
	d.clim_min_y = params['clim_min_y']#0 #expected limits
	d.clim_max_y = params['clim_max_y']#512 #expected limits
	d.digital_binning = params['digital_binning']#2 #Digital binning to apply (see below).
	d.cam_pixel_size = params['cam_pixel_size']#6.5 #um Fixed pixel size of camera
	d.objective_mag = params['objective_mag']#100
	d.objective_type = params['objective_type']#"Olympus UPlanSApo 1.4 NA Oil"
	d.camera_type = params['camera_type']#"Photometrics Prime sCMOS"
	d.lamp_type = params['lamp_type']#"CoolLED pE-300 Ultra"
	d.microscope_type = params['microscope_type']#"Olympus IX71"
	d.processor_type = platform.processor()
	d.computer_name =  socket.gethostname()
	
	d.analysis_method = params['analysis_method']
	d.algorithm_link = ""
	d.voxel_xy = (d.cam_pixel_size/d.objective_mag)*(d.digital_binning*d.cam_binning) #um
	print('d.voxel_xy',d.voxel_xy)
	d.z_stage_move = params['z_stage_move']#0.5 #um
	###Visualization.
	d.display_out = params['display_out']#False
	###Input and output.
	d.out_path = params['out_path']#e.g."/media/nvidia/DOXIE_SD/0004/"
	d.save_out = params['save_out']#"ij_tiff" #"ij_tiff" or "ome_tiff"
	d.positions_file_path = params['positions_file_path'] #"../pos_files/POS_FILE.txt"
	d.output_positions_name = params['output_positions_name']#"file_pos_export.txt"
	d.output_positions_file = d.out_path+"/"+d.output_positions_name
	d.exp_depth = params['exp_depth']
	###Output text description
	
	d.num_of_tpts = 6*48 #Total number of timepoints.
	d.mins_int = 10.0 #Time (minutes) to wait between each interval.
	d.int_for_refocus = 6 #Interval for recalculating focus (e.g. 6 represents on every sixth timepoint).
	d.focus_count = 10 #Number of slices above to acquire and number of slices below to acquire for initial focus.
	
	
	###Just some tests before we engage.
	assert d.ch_to_image <= d.exposures.__len__(), "please define channels to image <= number of exposures as channels to image."
	assert d.ch_to_save <= d.ch_to_image, "please define channels to save as <= channels to image."
	
	d.init_camera()
	if params['dkrepo'] != "":
		d.dkrepo = git.Repo(params['dkrepo']).head.object.hexsha
	else:
		d.dkrepo = ""
	
	d.algorithm_name = params['algorithm_name']#"YOLOv2 Darknet3 "
	d.config_path = params['config_path']#"../../darknet3AB/darknet/cfg/yolov2_dk3AB-classes-1-flip.cfg"
	d.meta_path =  params['meta_path']#"../../cell_datasets/cho_dapi_class/2020/obj_cho_dapi_class50.data"
	d.weight_path = params['weight_path']#"../../models/darknet/cho_dapi_class50/yolov2_dk3AB-classes-1-flip_final.weights" 
	
	
	
	focus_weight_path = "/home/nvidia/Documents/models/focus_model/model.ckpt-1000042"
	focus_model = prediction.ImageQualityClassifier(focus_weight_path,84,11)
	
	d.load_positions(d.positions_file_path)
	d.init_output_positions()
	
	### Loads the network in.
	if params['algorithm_name'] != "": 
		netMain = dk.load_net_custom(d.config_path.encode("ascii"), d.weight_path.encode("ascii"), 0, 1)
		metaMain = dk.load_meta(d.meta_path.encode("ascii"))
		
		d.output_wid = dk.network_width(netMain)
		d.output_hei = dk.network_height(netMain)
		darknet_image = dk.make_image(d.output_wid,d.output_hei,3)
	im = np.zeros((d.lim_max_y,d.lim_max_x,3)).astype(np.uint8)
	spa_sam = d.digital_binning 
	
	
	
	#####The main loop. This will keep going till all the stage positions have been visited.
	tfull = time.time()
	t0 = time.time()
	print("Running AMCA")
	
	
	starttime = time.time()
	for tp in range(0,d.num_of_tpts):
		if tp % d.int_for_refocus == 0 or tp == 0:
			print('run refocus')
			
			d.analysis_method = 'Focus'
			
		else:
			d.focus_count = 5 #Number of slices above and additionally below to acquire for subsequent focus calculation.
			print('close file')
			d.analysis_method = 'None'
			
			
		
		
		
		##time points.
		d.tp = tp
		
		d.pos_index = 0 
		#Query postion of stage x and y.
		d.on_move(d.pos_x[0],d.pos_y[0],d.pos_z[0])
		time.sleep(2)
		while True:
			## Collect frames and loops positions.
			
			t1 = time.time()
			if d.ch_to_image >= 1:
				CH1 = d.cam_aquire(d.exposures[0],None)
				if spa_sam == 1:
					frame_CH1 = CH1
				else:
					frame_CH1 = CH1[0::spa_sam,0::spa_sam]
					frame_CH1 += CH1[0::spa_sam,1::spa_sam]
					frame_CH1 += CH1[1::spa_sam,0::spa_sam]
					frame_CH1 += CH1[1::spa_sam,1::spa_sam]		
								
			if d.ch_to_image >= 2:
				CH2 = d.cam_aquire(d.exposures[1],None)
				if spa_sam == 1:
					frame_CH2 = CH2
				else:
					frame_CH2 = CH2[0::spa_sam,0::spa_sam]
					frame_CH2 += CH2[0::spa_sam,1::spa_sam]
					frame_CH2 += CH2[1::spa_sam,0::spa_sam]
					frame_CH2 += CH2[1::spa_sam,1::spa_sam]	
			if d.ch_to_image >= 3:
				CH3 = d.cam_aquire(d.exposures[2],None)
				if spa_sam == 1:
					frame_CH3 = CH3
				else:
					
					frame_CH3 = CH3[0::spa_sam,0::spa_sam]
					frame_CH3 += CH3[0::spa_sam,1::spa_sam]
					frame_CH3 += CH3[1::spa_sam,0::spa_sam]
					frame_CH3 += CH3[1::spa_sam,1::spa_sam]	
			
			
			assert d.lim_max_x == frame_CH1.shape[1], ('unusual x dimension', frame_CH1.shape[1])
			assert d.lim_max_y == frame_CH1.shape[0], ('unusual y dimension', frame_CH1.shape[0])
			t2 = time.time()
			
			
			
			###Converting into RGB format for CV object detection.
			if d.ch_to_analyze == 1:
				frame_CH1_n = (frame_CH1/np.max(frame_CH1))*255.0		
				im[:,:,0] = frame_CH1_n
				im[:,:,1] = frame_CH1_n
				im[:,:,2] = frame_CH1_n
			
			elif d.ch_to_analyze == 2:
				frame_CH1_n = (frame_CH1/np.max(frame_CH1))*255.0
				frame_CH2_n = (frame_CH2/np.max(frame_CH2))*255.0
				im[:,:,0] =frame_CH1_n
				im[:,:,1] =frame_CH2_n	
			
			elif d.ch_to_analyze.__len__() == 3:
				frame_CH1_n = (frame_CH1/np.max(frame_CH1))*255.0
				frame_CH2_n = (frame_CH2/np.max(frame_CH2))*255.0
				frame_CH3_n = (frame_CH3/np.max(frame_CH3))*255.0
				im[:,:,0] =frame_CH1_n
				im[:,:,1] =frame_CH2_n
				im[:,:,2] =frame_CH3_n
				
			if d.analysis_method == 'object':
				
				###Converted into correct dimension for darknet.	
				frame_resized = cv2.resize(im,(dk.network_width(netMain),dk.network_height(netMain)),interpolation=cv2.INTER_LINEAR)
				dk.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
				
				 
				
				t3 = time.time()
				detections = dk.detect_image(netMain, metaMain, darknet_image, thresh=0.50)
				if len(detections) > 0:
					#Save image to stack.
					if d.ch_to_save == 1:
						d.img_stk[d.stage_pos_z] = [frame_CH1]
					if d.ch_to_save == 2:
						d.img_stk[d.stage_pos_z] = [frame_CH1,frame_CH2]
					if d.ch_to_save == 3:
						d.img_stk[d.stage_pos_z] = [frame_CH1,frame_CH2,frame_CH3]
				t4 = time.time()
				out = analyzeAndMove(detections)
				t5 =time.time()

			if d.analysis_method == 'None':
				t3 = time.time()
				#Save image to stack.
				if d.ch_to_save == 1:
					d.img_stk[d.stage_pos_z] = [frame_CH1]
				if d.ch_to_save == 2:
					d.img_stk[d.stage_pos_z] = [frame_CH1,frame_CH2]
				if d.ch_to_save == 3:
					d.img_stk[d.stage_pos_z] = [frame_CH1,frame_CH2,frame_CH3]
				t4 = time.time()
				out = imageOnlyAndMove()
				t5 = time.time()
			if d.analysis_method == 'Focus':
				if d.ch_to_analyze == 1:
					imt = frame_CH1
			
				elif d.ch_to_analyze == 2:
					imt = frame_CH2	
				
				elif d.ch_to_analyze.__len__() == 3:
					imt = frame_CH3 
				
				focus_vals = focus_model.get_patch_predictions(imt)
				score = 0
				for val in focus_vals:
					opa = val[4].predictions
					score += opa
				
				t3 = time.time()
				#Save image to stack.
				if d.ch_to_save == 1:
					d.img_stk[d.stage_pos_z] = [frame_CH1]
				if d.ch_to_save == 2:
					d.img_stk[d.stage_pos_z] = [frame_CH1,frame_CH2]
				if d.ch_to_save == 3:
					d.img_stk[d.stage_pos_z] = [frame_CH1,frame_CH2,frame_CH3]
				t4 = time.time()
				out = focusAndMove(score)
				t5 = time.time()
			if d.analysis_method == 'Crop':
				
				imc = im[d.clim_min_y:d.clim_max_y,d.clim_min_x:d.clim_max_x,:]
				
			
				###Converted into correct dimension for darknet.	
				frame_resized = cv2.resize(imc,(dk.network_width(netMain),dk.network_height(netMain)),interpolation=cv2.INTER_LINEAR)
				dk.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
				
				t3 = time.time()
				detections = dk.detect_image(netMain, metaMain, darknet_image, thresh=0.50)
				print('detections',detections)
				if len(detections) > 0:
					#Save image to stack.
					if d.ch_to_save == 1:
						d.img_stk[d.stage_pos_z] = [frame_CH1]
					if d.ch_to_save == 2:
						d.img_stk[d.stage_pos_z] = [frame_CH1,frame_CH2]
					if d.ch_to_save == 3:
						d.img_stk[d.stage_pos_z] = [frame_CH1,frame_CH2,frame_CH3]
				t4 = time.time()
				out = analyzeAndMove(detections)
				t5 =time.time()
			
				
				
			
			timings_out ='Time (s), total: '+str(np.round(t5-t0,3))+' acquire: '+str(np.round(t2-t1,3))
			timings_out += ' detect: '+str(np.round(t4-t3,3))+' convert: '+str(np.round(t3-t2,3))
			timings_out += ' move: '+str(np.round(t5-t4,3))
			print(timings_out)
			t0 = time.time()
			if out == False:
				print('Session complete. Time taken (min): '+str(np.round((time.time()-tfull)/60,3)))
				break;
		
		if tp == 0:
			
			pass
			
		else:
			print ("will sleep for (s)",60*d.mins_int - ((time.time() - starttime) % 60))
			time.sleep(60*d.mins_int - ((time.time() - starttime) % 60))	
			
	
	d.cam.close()
	pvc.uninit_pvcam()

			
