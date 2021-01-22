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



#dataset_path = "../../cell_datasets/hek_peroxisome_class/2018/JPEGImages/"
#dataspec = dataset_path
#exp_def = "hek_peroxisome_class55"
#config_def = "yolov2_dk3AB-classes-1-flip"
#ext = '.jpg'

#dataset_path = "../../cell_datasets/erythroid_dapi_all_class/2019/JPEGImages/"
#dataspec = dataset_path
#exp_def = "erythroid_dapi_all_class51"
#config_def = "yolov2_dk3AB-classes-1-flip"
#ext = '.jpg'

dataset_path ="/Users/dominicwaithe/Documents/collaborators/SwiftLonnie/screens/acquisitions/0005_2020_11_27_low/images/"
dataspec = "/Users/dominicwaithe/Documents/collaborators/WaitheD/micro_vision/cell_datasets/cho_rfp_pcna_class/2020/"
exp_def = "cho_rfp_pcna_class50"
config_def = "yolov2_dk3AB-classes-1-flip"
ext = '.tif'


files_in_dir = [f for f in listdir(dataset_path) if isfile(join(dataset_path, f))]

out_File_folder = "/Users/dominicwaithe/Desktop/relabel05/"
config_path = "../../darknet3AB/darknet/cfg/"+config_def+".cfg"
meta_path =  dataspec+"obj_"+exp_def+".data"
weight_path = "/Users/dominicwaithe/Documents/collaborators/SwiftLonnie/screens/RFP-PCNA-yolov2_dk3AB-classes-1-flip_last.weights"
netMain = dk.load_net_custom(config_path.encode("ascii"), weight_path.encode("ascii"), 0, 1)
metaMain = dk.load_meta(meta_path.encode("ascii"))

channel = 1
file_pos = open( out_File_folder+'file_pos_export.txt','w')


for file in files_in_dir:
	imageFile = ".".join(file.split(".")[:-1])
	file_ext = file.split(".")[-1]
	if file != ".DS_Store" and "."+file_ext == ext:	
		#imageFile = file.split(".")[0]
		out_roiFile = imageFile+'all.svg'


		tfile = tifffile.TiffFile(dataset_path+imageFile+ext)

		

		strn = tfile.imagej_metadata['Info']
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
		img_shape = img_vol.shape

		if img_shape.__len__() > 3:
			slices =  img_shape[0]
			channels  = img_shape[1]
			height = img_shape[2]
			width = img_shape[3]
			print('img_shape',img_shape)
			data = []

			for sli_ind in range(0, slices):

				


				import_im = img_vol[sli_ind,channel,:,:]
				import_im = (import_im/np.max(import_im))*255.0
				im = np.zeros((height,width,3))
				im[:,:,0] = import_im
				im[:,:,1] = import_im
				im[:,:,2] = import_im

				im = im.astype(np.uint8)
				output_wid = dk.network_width(netMain)
				output_hei = dk.network_height(netMain)
				darknet_image = dk.make_image(output_wid,output_hei,3)
				frame_resized = cv2.resize(im,(output_wid,output_hei),interpolation=cv2.INTER_LINEAR)

				dk.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
				detections = dk.detect_image(netMain, metaMain, darknet_image, thresh=0.50)
				#print('detections',detections)
				
				for detect in detections:
					print(detect)
					a = np.clip((detect[2][0]-detect[2][2]//2)/output_wid*import_im.shape[1],0,import_im.shape[1])
					b = np.clip((detect[2][1]-detect[2][3]//2)/output_hei*import_im.shape[0],0,import_im.shape[0])
					c = np.clip(detect[2][2]/output_wid*import_im.shape[1],0,import_im.shape[1])
					d = np.clip(detect[2][3]/output_hei*import_im.shape[0],0,import_im.shape[0])
					roi_b = Roi(a, b, c, d, im.shape[0], im.shape[1], 0)
					roi_b.name = "Region 1"
					roi_b.roiType = 1
					#roi_b.position = 10
					#roi_b.channel = channel+1
					roi_b.setPositionH(  channel+1, sli_ind, 0)

					roi_b.strokeLineWidth = 3.0
					roi_b.strokeColor = RGB_encoder(255, 0, 255, 255)
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

					file_pos.writelines(str(stage_pos_x)+","+str(stage_pos_y)+","+str(stage_pos_z[sli_ind])+","+str(xoutpos)+","+str(youtpos)+","+str(woutpos)+","+str(houtpos)+","+str(score)+"\n")


			
		metadata = {'hyperstack': True ,'channels':3, 'ImageJ': '1.52g', 'Overlays':data , 'loop': False}

		tifffile.imsave(out_File_folder+imageFile+"all.tiff", img_vol, shape=im.shape, imagej=True, ijmetadata=metadata)
		

file_pos.close()