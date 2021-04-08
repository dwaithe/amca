
import pylab as plt
#darknet3AB import
import sys
sys.path.append("../../darknet3AB/darknet")
import darknet as dk
import matplotlib.pylab as plt
import numpy as np
import cv2
from ijroi.ij_roi import Roi
from ijroi.ijpython_encoder import encode_ij_roi,  RGB_encoder
import tifffile
from os import listdir
from os.path import isfile, join
import det_sort as ds

from convert_ROI_to_cell_volumes import *
from ijroi.ij_roi import Roi
from ijroi.ijpython_encoder import encode_ij_roi,RGB_encoder
from ijroi.ijpython_decoder import decode_ij_roi





def compute_focus(file_pos_path,dataset_path,tp):
	files_in_dir = [f for f in listdir(dataset_path) if isfile(join(dataset_path, f))]
	pos_file_rtn = file_pos_path.split('.txt')[0]+str(tp)+'.txt'
	f = open(pos_file_rtn,'w')
	for filename in files_in_dir:
		
		if str(tp).zfill(4) in filename:

			input_file = dataset_path+filename
			tfile = tifffile.TiffFile(input_file)
			img_stk = tfile.asarray()
			img_shape = img_stk.shape
			
			if img_stk.shape.__len__() > 2:
				pass
			else:
				continue;
			
			ch = 0


			roi_array = return_overlay(tfile)
			c = 0
			trk_mat = np.zeros((8,roi_array.__len__())).astype(np.float64) 
			for z in range(0,img_stk.shape[0]):
				if img_stk.shape.__len__()>3:
				   im = img_stk[z,ch,:,:]
				elif img_stk.shape.__len__()==3:
				   im = img_stk[z,:,:]
				
			    #plt.figure()
			    #plt.imshow(im)
			   
				for roi in roi_array:

					if roi.position == z+1 or roi.slice == z+1:
						  rx0 = roi.x
						  rx1 = roi.x+roi.width
						  ry0 = roi.y
						  ry1 = roi.y+roi.height
						  prob = float(roi.name.replace('\x00', '').split('-')[-1])
						  R = (np.random.random())  # same random number as before
						  G = (np.random.random())  # same random number as before
						  B = (np.random.random()) # same random number as before
						  plt.plot([rx0,rx0,rx1,rx1,rx0],[ry0,ry1,ry1,ry0,ry0],'r-')
						  trk_mat[:,c] = [0,0,z+1,rx0,ry0,rx1,ry1,prob]
						  
						  c+=1

			in_results = []
			out_results = []


			trks = np.array(trk_mat)
			mot_tracker = []
			mot_tracker = ds.Sort(max_age=100,min_hits=0)

			mot_tracker.trackers = []
			mot_tracker.frame_count = 0

			trackers = None
			for z in range(0,img_stk.shape[0]):
				ind = np.where(trks[2,:] == z)[0]
				trs = trks[:,ind]

				dets = []
				max_prob = []
				for c in range(0,trs.shape[1]):
					x1 = trs[3,c]
					y1 = trs[4,c]
					max_prob.append(trs[7,c])
				   
					x2 = (trs[5,c])
					y2 = (trs[6,c])
					detstxt = np.array([x1,y1,x2,y2]).astype(np.float64)
					dets.append(detstxt)
			    
				if dets.__len__() == 0 or dets[0].__len__() >0:
				   trackers = mot_tracker.update(np.array(dets))
				trackers_wz = []
				for track in trackers:
				   trackers_wz.append(np.append(track.astype(np.float64),[z,np.max(max_prob)]))
				out_results.extend(trackers_wz)
			    

			out_results = np.array(out_results)

			
			ids = np.unique(out_results[:,4])
			out_out =[]
			for idt in ids:
				idx = np.where(out_results[:,4] == idt)
				if idx[0].shape[0] >2:
					for idx0 in idx[0]:
						out_out.append(out_results[idx0,:])

			final_out = np.array(out_out).T
			best_mag = int(out_out[np.argmax(np.array(out_out)[:,6])][5])


		

			

			#Get existing metadata
			metadata = tfile.imagej_metadata
			
			strn = metadata['Info']
			lines = strn.split("\n")
			for entry in lines:
				if entry[:12] == 'Stage X-pos:':
					stage_pos_x = float(entry.split(":")[1].split("um.")[0])
				if entry[:12] == 'Stage Y-pos:':
					stage_pos_y = float(entry.split(":")[1].split("um.")[0])
				if entry[:11] == 'XY-spacing:':
					voxel_xy = float(entry.split(":")[1].split("um, Z-spacing")[0])
				if entry[:12] == 'Piezo Z-pos:':
					stage_pos_z = list(np.array(entry.split(":")[1].split(", (um)")[0].split(',')).astype(np.float64))
					stage_pos_z.sort()
			print('z-index',stage_pos_z[best_mag])	
			

			im_stk = tfile.asarray()
			f.write(str(stage_pos_x)+"\t"+str(stage_pos_y)+"\t"+str(stage_pos_z[best_mag])+'\n')

	f.close()
	return pos_file_rtn
