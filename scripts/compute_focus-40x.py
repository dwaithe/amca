
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
sys.path.append('../src')
import det_sort as ds

from convert_ROI_to_cell_volumes import *
from ijroi.ij_roi import Roi
from ijroi.ijpython_encoder import encode_ij_roi,RGB_encoder
from ijroi.ijpython_decoder import decode_ij_roi



dataspec = "../../cell_datasets/cho_rfp_pcna_class/2020/"
exp_def = "cho_rfp_pcna_class50"
config_def = "yolov2_dk3AB-classes-1-flip"
ext = '.tif'



config_path = "../../darknet3AB/darknet/cfg/"+config_def+".cfg"
meta_path =  dataspec+"obj_"+exp_def+".data"
weight_path = "/home/nvidia/Documents/models/darknet/U2OS_RFP_class50/RFP-PCNA-yolov2_dk3AB-classes-1-flip_last.weights"
netMain = dk.load_net_custom(config_path.encode("ascii"), weight_path.encode("ascii"), 0, 1)
metaMain = dk.load_meta(meta_path.encode("ascii"))

channel = 1






dataset_path ="/media/nvidia/Dominic/prescan/"
out_File_folder =  '/media/nvidia/Dominic/scanned/'
out_File_folder2 = '/media/nvidia/Dominic/processed/'
files_in_dir = [f for f in listdir(dataset_path) if isfile(join(dataset_path, f))]

output_wid = dk.network_width(netMain)
output_hei = dk.network_height(netMain)
darknet_image = dk.make_image(output_wid,output_hei,3)

f = open(out_File_folder2+'POS_FILE.txt','w')

for file in files_in_dir:
	imageFile = ".".join(file.split(".")[:-1])
	file_ext = file.split(".")[-1]
	if file != ".DS_Store" and "."+file_ext == ext:	
		#imageFile = lfile.split(".")[0]
		out_roiFile = imageFile+'all.svg'
        

		tfile = tifffile.TiffFile(dataset_path+imageFile+ext)


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
				print('spz',stage_pos_z)

		assert stage_pos_x, "The metadata was not read properly"

		img_vol =  tfile.asarray()
		tfile.close()
		img_shape = img_vol.shape

		if img_shape.__len__() > 3:
			slices =  img_shape[0]
			channels  = img_shape[1]
			height = 410
			width = 410
		else:
			slices =  img_shape[0]
            
			height = 410
			width = 410
            
            
		data = []

		for sli_ind in range(0,slices):
			cly = [0,307,614]
			clx = [0,307,614]
                
			for i in range(0,cly.__len__()):
				for j in range(0,clx.__len__()):
					clim_min_y = cly[i]
					clim_max_y = clim_min_y+410
					clim_min_x = clx[j]
					clim_max_x = clim_min_x+410
                
					if img_shape.__len__() > 3:
						import_im = img_vol[sli_ind,channel,clim_min_y:clim_max_y,clim_min_x:clim_max_x]
					else:
						import_im = img_vol[sli_ind,clim_min_y:clim_max_y,clim_min_x:clim_max_x]

					import_im = (import_im/np.max(import_im))*255.0
					im = np.zeros((height,width,3))
					im[:,:,0] = import_im
					im[:,:,1] = import_im
					im[:,:,2] = import_im

					im = im.astype(np.uint8)
					
					frame_resized = cv2.resize(im,(output_wid,output_hei),interpolation=cv2.INTER_LINEAR)

					dk.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
					detections = dk.detect_image(netMain, metaMain, darknet_image, thresh=0.50)
					print('detections',detections)

					for detect in detections:
						print(detect)
						a = np.clip((detect[2][0]-detect[2][2]//2)/output_wid*import_im.shape[1],0,import_im.shape[1])+clim_min_x
						b = np.clip((detect[2][1]-detect[2][3]//2)/output_hei*import_im.shape[0],0,import_im.shape[0])+clim_min_y
						c = np.clip(detect[2][2]/output_wid*import_im.shape[1],0,import_im.shape[1])
						d = np.clip(detect[2][3]/output_hei*import_im.shape[0],0,import_im.shape[0])
						roi_b = Roi(a, b, c, d, im.shape[0], im.shape[1], 0)
						roi_b.name = "Region-1-p-"+str(detect[1])
						roi_b.roiType = 1
						#roi_b.position = 10
						#roi_b.channel = channel+1
						roi_b.setPosition(sli_ind+1)

						roi_b.strokeLineWidth = 3.0
						roi_b.strokleColor = RGB_encoder(255, 0, 255, 255)
						data.append(encode_ij_roi(roi_b))
						xmin = int(round(a - (c / 2)))
						xmax = int(round(a + (c / 2)))
						ymin = int(round(b - (d / 2)))
						ymax = int(round(b + (d / 2)))
						score = detect[1]

						xoutpos = voxel_xy*a
						youtpos = voxel_xy*b
						woutpos = voxel_xy*d
						houtpos = voxel_xy*c
		metadata['Overlays'] = data
		
		tifffile.imsave(out_File_folder+file, img_vol, shape=im.shape, imagej=True, ijmetadata=metadata)
		

files_in_dir = [f for f in listdir(dataset_path) if isfile(join(dataset_path, f))]
for filename in files_in_dir:
	

	input_file = out_File_folder+filename
	output_file = out_File_folder2+filename
	tfile = tifffile.TiffFile(input_file)
	img_stk = tfile.asarray()
	img_shape = img_stk.shape
	ch = 0


	roi_array = return_overlay(tfile)
	c = 0
	trk_mat = np.zeros((8,roi_array.__len__())).astype(np.float64) 
	for z in range(0,img_stk.shape[0]):
		if img_stk.shape.__len__()>3:
		   im = img_stk[z,ch,:,:]
		else:
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
	    #roiX0,roiY0,roiX1,roiY1,uniqueID,stagex,stagey,stagez

	out_results = np.array(out_results)

	#Correct regions to be same size.
	ids = np.unique(out_results[:,4])
	out_out =[]
	for idt in ids:
		idx = np.where(out_results[:,4] == idt)
		if idx[0].shape[0] >2:

			out_results[idx,0] = np.average(out_results[idx,0])
			out_results[idx,1] = np.average(out_results[idx,1])
			out_results[idx,2] = np.average(out_results[idx,2])
			out_results[idx,3] = np.average(out_results[idx,3])
			for idx0 in idx[0]:
				out_out.append(out_results[idx0,:])

	final_out = np.array(out_out).T
	best_mag = int(out_out[np.argmax(np.array(out_out)[:,6])][5])
	print(best_mag)

	tfile = tifffile.TiffFile(input_file)


	trks = final_out
	data = []

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
	#Get existing image-data.

	im_stk = tfile.asarray()
	f.write(str(stage_pos_x)+"\t"+str(stage_pos_y)+"\t"+str(stage_pos_z[best_mag])+'\n')



	#Run through each region in the image.
	for trk in range(0,trks.shape[1]):

		trkv = trks[:,trk]
		x0 = trkv[0]

		y0 = trkv[1]

		wid = trkv[2]-x0
		hei = trkv[3]-y0


	    #Inititate each region.
		roi_b = Roi(x0,y0, wid, hei, 1024, 1024,0)
		roi_b.name = "Region-"+str(int(trkv[4]))
		roi_b.roiType = 1

	    

		roi_b.position = int(trkv[5])

	    

	    

		roi_b.strokeLllineWidth = 3.0
		#Colours each volume-region uniquely.
		np.random.seed(int(trkv[4]))
		if roi_b.position == best_mag:
			roi_b.strokeColor = RGB_encoder(255,255,255,255)
		else:
			roi_b.strokeColor = RGB_encoder(255,np.random.randint(0, 255),np.random.randint(0, 255),np.random.randint(0, 255))
	    
		data.append(encode_ij_roi(roi_b))
	metadata['Overlays'] = data
	tifffile.imsave(output_file,im_stk, shape=im_stk.shape, imagej=True, ijmetadata=metadata)
	tfile.close()
f.close()
