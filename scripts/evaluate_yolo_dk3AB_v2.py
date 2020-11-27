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

dataset_path ="../../cell_datasets/acquisitions/20200413_10x/small/"
dataspec = "../../cell_datasets/cos7_nucleopore_class/2019/"
exp_def = "cos7_nucleopore_class50"
config_def = "yolov2_dk3AB-classes-1-flip"
ext = '.jpg'


files_in_dir = [f for f in listdir(dataset_path) if isfile(join(dataset_path, f))]

out_File_folder = "/scratch/dwaithe/models/darknet/out_imgs/"
config_path = "../../darknet3AB/darknet/cfg/"+config_def+".cfg"
meta_path =  dataspec+"obj_"+exp_def+".data"
weight_path = "/scratch/dwaithe/models/darknet/"+exp_def+"/"+config_def+"_final.weights"
netMain = dk.load_net_custom(config_path.encode("ascii"), weight_path.encode("ascii"), 0, 1)
metaMain = dk.load_meta(meta_path.encode("ascii"))

for file in files_in_dir:
	imageFile = file.split(".")[0]
	file_ext = file.split(".")[-1]
	if file != ".DS_Store" and "."+file_ext == ext:	
		#imageFile = file.split(".")[0]
		out_roiFile = imageFile+'all.svg'

		import_im = plt.imread(dataset_path+imageFile+ext)
		import_im = (import_im/np.max(import_im))*255.0
		im = np.zeros((import_im.shape[0],import_im.shape[1],3))
		im[:,:,0] = import_im
		im[:,:,1] = import_im
		im[:,:,2] = import_im

		im = im.astype(np.uint8)
		output_wid = dk.network_width(netMain)
		output_hei = dk.network_height(netMain)
		print(im.shape)
		darknet_image = dk.make_image(output_wid,output_hei,3)
		frame_resized = cv2.resize(im,(output_wid,output_hei),interpolation=cv2.INTER_LINEAR)

		dk.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
		detections = dk.detect_image(netMain, metaMain, darknet_image, thresh=0.50)
		#print('detections',detections)
		data = []

		f= open(out_File_folder+out_roiFile,"w+")
		svg_out = "<svg width=\""+str(import_im.shape[1])+"\" height=\""+str(import_im.shape[0])+"\">\n"
		for detect in detections:
			print(detect)
			a = np.clip((detect[2][0]-detect[2][2]//2)/output_wid*import_im.shape[1],0,import_im.shape[1])
			b = np.clip((detect[2][1]-detect[2][3]//2)/output_hei*import_im.shape[0],0,import_im.shape[0])
			c = np.clip(detect[2][2]/output_wid*import_im.shape[1],0,import_im.shape[1])
			d = np.clip(detect[2][3]/output_hei*import_im.shape[0],0,import_im.shape[0])
			roi_b = Roi(a, b, c, d, im.shape[0], im.shape[1], 0)
			roi_b.name = "Region 1"
			roi_b.roiType = 1
			roi_b.position = 10
			roi_b.strokeLineWidth = 3.0
			roi_b.strokeColor = RGB_encoder(255, 0, 255, 255)
			data.append(encode_ij_roi(roi_b))
			svg_out += "<g><path d=\'m"
			svg_out += " "+str(int(a))+","+str(int(b))+" "+str(int(c))+","+str(0)+" "+str(0)+","+str(int(d))+" "+str(int(0-c))+","+str(0)+ " z'/></g>" "\n"
			
		svg_out += "</svg>"
		f.write(svg_out)
		f.close()
		print(svg_out) 
		metadata = {'hyperstack': True ,'channels':3, 'ImageJ': '1.52g', 'Overlays':data , 'loop': False}

		tifffile.imsave(out_File_folder+imageFile+"all.tiff", im, shape=im.shape, imagej=True, ijmetadata=metadata)