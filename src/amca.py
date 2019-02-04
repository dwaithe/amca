#!/usr/bin/env python

# --------------------------------------------------------
# Tensorflow Faster R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Xinlei Chen, based on code from Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import sys 
sys.path.append("C:/Users/immuser/Documents/micro_vision/Faster-RCNN-TensorFlow-Python3.5-master/")
sys.path.append("C:/Users/immuser/Documents/micro_vision/ijpython_roi")
from lib.config import config as cfg
from lib.utils.nms_wrapper import nms
from lib.utils.test import im_detect
#from nets.resnet_v1 import resnetv1
from lib.nets.vgg16 import vgg16
from lib.utils.timer import Timer
import time as time
import matplotlib.pyplot as plt
import numpy as np
import time
from control.stageXY_control import*
import control.zpiezoPI as zpi
import tifffile
import sys
sys.path.append('ijpython_roi')
from ij_roi import Roi
from ijpython_encoder import encode_ij_roi, RGB_encoder

from ctypes import cdll

axis = '3'
verbose = 1

pidll = cdll.LoadLibrary('c:/Users/immuser/Documents/E710_GCS_DLL/E7XX_GCS_DLL_x64.dll')
ID = pidll.E7XX_ConnectRS232(5,57600)

zpi.initiate_axis(pidll,ID, axis,verbose)
zpi.turn_servo_on(pidll,ID,axis,verbose)
zpi.check_for_errors(pidll,verbose)
zpi.query_position(pidll,ID,axis,verbose)
import cv2


try:
	# This will create a new file or **overwrite an existing file**.
	fout = open("file_pos_export.txt", "w")
	
except: 
	IOError



ms = MS2000(which_port='COM1', verbose=False)
xyz = XYZStage(ms2000_obj=ms, axes=('X', 'y'),verbose=False)


plt.ion()
class DynamicUpdate():
	def __init__(self):

		self.img_stk = {}
		self.description = {}
		self.pos_x = []
		self.pos_y = []
		self.pos_z = []
		self.regions = {}
		with open('POS_FILE.txt', 'r') as f:

			for line in f:
				items = line.split('\t')
				self.pos_x.append(float(items[0]))
				self.pos_y.append(float(items[1]))
				self.pos_z.append(float(items[2].split('\n')[0]))
		print('file positions loaded.')

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


		#Query postion of stage x and y.
		self.pos = xyz.get_position()
		self.on_move(self.pos_x[0],self.pos_y[0],self.pos_z[0])
	
		#float(zpi.query_position(pidll,ID,axis,verbose=True))

	

	def on_launch(self):
		#Set up plot
		self.figure, self.ax = plt.subplots()
		thismanager = plt.get_current_fig_manager()
		sxpos = 2050
		sypos = 59
		swpos = 569
		shpos = 498
		#(2171, 123, 332, 371)
		thismanager.window.setGeometry(sxpos+8, sypos+31, swpos-16, shpos-39)
		self.lines, = self.ax.plot([],[], '-')
		self.figure.patch.set_facecolor('black')
		self.ax.set_axis_bgcolor("black")
		

				#Autoscale on unknown axis and known lims on the other
		self.ax.set_autoscaley_on(True)
		self.ax.set_xlim(self.lim_min_x, self.lim_max_x)
		self.ax.set_ylim(self.lim_min_y, self.lim_max_y)
		#Other stuff
		self.ax.grid()
		#...

	def on_running_test(self, xdata, ydata):
		#Update data (with the new _and_ the old points)
		self.lines.set_xdata(xdata[-4:])
		self.lines.set_ydata(ydata[-4:])
		
		#Need both of these in order to rescale
		self.figure.canvas.draw()
		self.figure.canvas.flush_events()
	def on_running(self,scores,boxes,thresh,NMS_THRESH,intensity_score,save_boxes):
		sf = 3.4 #This is the ratio for correcting the visual output to the correct size.
		frame = np.zeros((int(512./sf),int(512./sf),3),np.uint8)
		key = cv2.waitKey(1)
		self.regions[self.stage_pos_z] = []
		cls_ind = self.class_to_sample
				
		cls_boxes = boxes[:, 4 * cls_ind:4 * (cls_ind + 1)]
		cls_scores = scores[:, cls_ind]
		dets = np.hstack((cls_boxes,cls_scores[:, np.newaxis])).astype(np.float32)
		keep = nms(dets, NMS_THRESH)
		self.dets = dets[keep, :]
		intensity_score = intensity_score[keep]

		# These are bigger regions which predict into adjacent image regions.
		#save_cls_boxes = save_boxes[:, 4 * cls_ind:4 * (cls_ind + 1)]
		#save_dets = np.hstack((save_cls_boxes,cls_scores[:, np.newaxis])).astype(np.float32)
		#self.save_dets = save_dets[keep,:]
		
		
		
		self.inds = np.where(self.dets[:, -1] >= thresh)[0]
		
		

		if len(self.inds) > 0:
			for i in self.inds:
				bbox = self.dets[i, :4]
				score = self.dets[i, -1]
				intensity = intensity_score[i]
				#cv2.rectangle(im, (bbox[0],bbox[1]), (bbox[2],bbox[3]), (255,0,0), 3)
				#self.ax.plot((bbox[0],bbox[1],bbox[1],bbox[0]),(bbox[2],bbox[3],bbox[2],bbox[3]))
				hei = bbox[3] - bbox[1]
				wid = bbox[2] - bbox[0]
				#self.ax.add_patch(plt.Rectangle((bbox[0], self.lim_max_y-bbox[1]-hei),wid,hei, fill=False,edgecolor='red', linewidth=3.5))

				cvx = int(bbox[0]/sf)
				cvy = int((self.lim_max_y-bbox[1]-hei)/sf)
				cvw = int(cvx+(wid/sf))
				cvh = int(cvy+(hei/sf))

				cv2.rectangle(frame, (cvx,cvy),(cvw,cvh), (0,255,0),1)
				self.regions[self.stage_pos_z].append([bbox[0],bbox[1],wid,hei])

				#Now we are exporting the save regions. These are bigger regions which predict into adjacent image regions.
				
				#sbbox = self.save_dets[i, :4]
				#if np.sum(np.array(sbbox)-np.array(bbox))!=0:
				#	print('sbbox',np.array(sbbox),'bbox',np.array(bbox))
				
				hei = bbox[3] - bbox[1]
				wid = bbox[2] - bbox[0]
				xoutpos = self.voxel_xy*bbox[0]
				youtpos = self.voxel_xy*bbox[1]
				woutpos = self.voxel_xy*wid
				houtpos = self.voxel_xy*hei
				
				fout.writelines(str(self.stage_pos_x)+","+str(self.stage_pos_y)+","+str(self.stage_pos_z)+","+str(xoutpos)+","+str(youtpos)+","+str(woutpos)+","+str(houtpos)+","+str(score)+"\n")			
				#Need both of these in order to rescale
		
		cv2.imshow('frame',frame)
		

	def on_move(self,stage_move_x,stage_move_y,stage_move_z):
		self.stage_pos_x = stage_move_x
		self.stage_pos_y = stage_move_y
		self.stage_pos_z = stage_move_z
		
		print('xyz',self.stage_pos_x,self.stage_pos_y,self.stage_pos_z)
		xyz.move(x_um = self.stage_pos_x, y_um = self.stage_pos_y, blocking=False)
		zpi.move_piezo(pidll,ID,axis,self.stage_pos_z,verbose)
		
		#print("set_xyz",self.stage_pos_x, self.stage_pos_y, self.stage_pos_z)
		#print("act_xyz",zpi.query_position(pidll,ID,axis,verbose=True))

	#Example
	def __call__(self):
		
		self.on_launch()
		#xdata = []
		#ydata = []
		#for x in np.arange(0,100,0.5):
		#    xdata.append(x)
		#    ydata.append(np.exp(-x**2)+10*np.exp(-(x-7)**2))
		#    self.on_running(xdata, ydata)
			
		#return xdata, ydata

d = DynamicUpdate()
d()

CLASSES = ('__background__',
											'aeroplane', 'bicycle', 'bird', 'boat',
											'bottle', 'bus', 'car', 'cat', 'chair',
											'cow', 'diningtable', 'dog', 'horse',
											'motorbike', 'person', 'pottedplant',
											'sheep', 'sofa', 'train', 'tvmonitor','cell')

NETS = {'vgg16': ('vgg16_faster_rcnn_iter_15000.ckpt',), 'res101': ('res101_faster_rcnn_iter_110000.ckpt',)}
d.CLASSES = ('__background__', 'cell - neuroblastoma phalloidin','cell - erythroblast dapi','cell - c127 dapi', 'cell - eukaryote dapi','cell - fibroblast nucleopore','cell - hela peroxisome all')
d.class_to_sample = 3
NETS = {'C127': ('vgg16_faster_rcnn_iter_20000.ckpt',)}
DATASETS = {'pascal_voc': ('voc_2007_trainval',), 'pascal_voc_0712': ('voc_2007_trainval+voc_2012_trainval',)}
xdata = []
ydata = []

sf =2
frame = np.zeros((int(512./sf),int(512./sf),3),np.uint8)
cv2.imshow('frame',frame)
d.t1 = time.time()




def analyzeAndMove(arr):
	"""Detect object classes in an image using pre-computed object proposals."""

	
	#
	#image_name = '000456.jpg'

	# Load the demo image
	#im_file = os.path.join(cfg.FLAGS2["data_dir"], 'demo', image_name)
	
	if arr.shape[0] == 1024*1024:
		im = np.zeros((1024,1024,3))
		imput = np.array(arr).reshape(1024,1024)
	elif arr.shape[0] == 512*512:
		im = np.zeros((512,512,3))
		imput = np.array(arr).reshape(512,512)
	else:
		print ('arrshape',arr.shape[0])
	#opp = cv2.imread(im_file)
	#print(opp.shape)
	
	im[:,:,0] =imput
	im[:,:,1] =imput
	im[:,:,2] =imput
	
	im = (im/np.max(im))*255.0
	


	
	delay = False
	#im = opp
	# Detect all object classes and regress object bounds
	
	print("time:",time.time()-d.t1)
	
	d.t1 = time.time()
	scores, boxes, save_boxes = im_detect(sess, net, im[:,:,:])
	intensity_score = []
	for bbox in boxes:
		
		intensity_score.append(np.sum(im[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2]),0]))
	if intensity_score.__len__()>0:
		intensity_score = np.array(intensity_score)
		intensity_score = (intensity_score/np.max(intensity_score))*255.

	#timer.toc()
	#print('time',time.time(),'Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0]))

	# Visualize detections for each class
	thresh = 0.5
	NMS_THRESH = 0.5
	d.on_running(scores,boxes,thresh,NMS_THRESH,intensity_score,save_boxes)

	plt.ioff()
	plt.figure()
	currentAxis = plt.gca()
	plt.imshow(imput)
	
	if len(d.inds) > 0:
		#Save image to stack.
		d.img_stk[d.stage_pos_z] = imput

	#print('d.naive',d.naive,'d.inds',d.inds)
	if d.naive == True:
		if len(d.inds) > 0:
			#This is the first time this image is seen and we have detected regions. 
			d.description[d.stage_pos_z] = []
			for i in d.inds:
				bbox = d.dets[i, :4]
				score = d.dets[i, -1]
				hei = bbox[3] - bbox[1]
				wid = bbox[2] - bbox[0]
				#currentAxis.add_patch(plt.Rectangle((bbox[0], bbox[1]), wid, hei, fill=False, edgecolor='red', linewidth=3.5))
				d.description[d.stage_pos_z].append(str(score)+','+str(bbox[0])+','+str(bbox[1])+','+str(wid)+','+str(hei))
			
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
			
			if len(d.inds) > 0:
				d.description[d.stage_pos_z] = []
				for i in d.inds:
					bbox = d.dets[i, :4]
					score = d.dets[i, -1]
					hei = bbox[3] - bbox[1]
					wid = bbox[2] - bbox[0]
					#currentAxis.add_patch(plt.Rectangle((bbox[0], bbox[1]), wid, hei, fill=False, edgecolor='red', linewidth=3.5))
					d.description[d.stage_pos_z].append(str(score)+','+str(bbox[0])+','+str(bbox[1])+','+str(wid)+','+str(hei))
			else:
				#If there are no more regions.
				if d.scanning_up == True and d.scanning_down == False:
					print('changeing direction.')
					d.scanning_down = True
					d.scanning_up = False
					d.z_index = 1
					delay = True
				
				elif d.scanning_up == False and d.scanning_down == True:
					#print('direction changed.')
					d.scanning_down = False
					d.scanning_up = False
					d.naive = True
					d.z_index = 1
					d.pos_index += 1

					names = []
					for name in d.img_stk:
						names.append(float(name))
					names.sort()

					#print("names",names)
					np_stk = np.zeros((len(names),d.lim_max_y,d.lim_max_x)).astype(np.float32)
					c = 0
					
					data = []
					for name in names:
						np_stk[c,:,:] = d.img_stk[name]
						regions = d.regions[name]
						
						c+=1
					
						for reg in regions:

							roi_b = Roi(reg[0],reg[1],reg[2],reg[3], np_stk.shape[1],np_stk.shape[2],0)
							roi_b.name = "Region 1"
							roi_b.roiType = 1
							roi_b.position = c
							roi_b.strokeLineWidth = 3.0
							roi_b.strokeColor = RGB_encoder(255,255,0,0)
							data.append(encode_ij_roi(roi_b))

					metadata = {'hyperstack': True ,'ImageJ': '1.52g', 'Overlays':data , 'loop': False}
					tifffile.imsave("C:/Users/immuser/Documents/micro_vision/out/img_stk_x_"+str(d.stage_pos_x)+"y_"+str(d.stage_pos_y)+".tif",np_stk,shape=np_stk.shape,imagej=True,ijmetadata=metadata)
					d.img_stk = {}
					d.regions = {}
				
	
	#If we find regions then scan above and below until they are done.
	
					
	#plt.savefig('out/out'+str(time.time())+'.tif')
	plt.close()
		#ax.add_patch(plt.Rectangle((bbox[0], bbox[1]),bbox[2] - bbox[0],bbox[3] - bbox[1], fill=False,edgecolor='red', linewidth=3.5))"""
	#plt.show()
								
	#im[0:240,0:240,0] = 255
	
	#cv2.imwrite('out'+str(time.time())+'.tif',im)


	
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
def parse_args():
	"""Parse input arguments."""
	parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
	parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16 res101]',
																					choices=NETS.keys(), default='res101')
	parser.add_argument('--dataset', dest='dataset', help='Trained dataset [pascal_voc pascal_voc_0712]',
																					choices=DATASETS.keys(), default='pascal_voc_0712')
	args = parser.parse_args()

	return args



args = parse_args()
			

# model path
demonet = 'C127'
dataset = args.dataset
tfmodel = os.path.join('C:/Users/immuser/Documents/micro_vision/Faster-RCNN-TensorFlow-Python3.5-master/output', demonet, DATASETS[dataset][0], 'default', NETS[demonet][0])

if not os.path.isfile(tfmodel + '.meta'):
				print(tfmodel)
				raise IOError(('{:s} not found.\nDid you download the proper networks from '
																			'our server and place them properly?').format(tfmodel + '.meta'))

# set config
tfconfig = tf.ConfigProto(allow_soft_placement=True)
tfconfig.gpu_options.allow_growth = True

# init session
sess = tf.Session(config=tfconfig)
# load network
#if demonet == 'vgg16':
net = vgg16(batch_size=1)
# elif demonet == 'res101':
				# net = resnetv1(batch_size=1, num_layers=101)
#else:
#    raise NotImplementedError
net.create_architecture(sess, "TEST", d.CLASSES.__len__() ,tag='default', anchor_scales=[8, 16, 32])#Change the third argument to represent number of classes.
#saver = tf.train.Saver()
saver = tf.train.Saver()
saver.restore(sess, tfmodel)

print('Loaded network {:s}'.format(tfmodel))

im_names = ['000456.jpg', '000457.jpg', '000542.jpg', '001150.jpg',
												'001763.jpg', '004545.jpg']

# demo()


			