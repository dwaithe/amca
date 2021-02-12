#For this we need the libary: https://github.com/dwaithe/ijpython_roi
from ijroi.ij_roi import Roi
from ijroi.ijpython_encoder import encode_ij_roi, RGB_encoder
import numpy as np
import tifffile
import os
from datetime import datetime
#TZCYX

def saveas_imagej_tiff(im_stk, stack_rois,d):
	lets_get_meta =[]
	width = im_stk.shape[4]
	height = im_stk.shape[3]
	
	print('Saving img stack of dims: ',im_stk.shape)
	for regions,z in stack_rois:
		for reg in regions:
							
			r0 = np.clip(reg[0],0,width)
			r1 = np.clip(reg[1],0,height)
			r2 = np.clip(reg[2],0,width)
			r3 = np.clip(reg[3],0,height)
			roi_b = Roi(r0,r1,r2,r3, width,height,0)
			roi_b.name = "Region-1-p-"+str(reg[4])
			roi_b.roiType = 1
			if d.ch_to_save == 1:
				roi_b.setPosition(z)
			else:
				roi_b.setPositionH(1,z+1,-1) #channel, sliceZ, frame
				
			roi_b.strokeLineWidth = 1.0
			roi_b.strokeColor = RGB_encoder(255,255,0,0)
			lets_get_meta.append(encode_ij_roi(roi_b))


	metadata = {'hyperstack': True } 
	metadata['mode'] = 'composite'
	metadata['unit'] = 'um'
	metadata['spacing'] = d.z_stage_move #This is the z-spacing of the image-stack  (for unit see 'unit').
	metadata['min']= 0.0
	metadata['max']= 0.0
	
	info = "-----------------------\n"
	info += "AMCA - Automated Microscope Control Algorithm.py. \n"
	info += "-----------------------\n"
	info += "Software by Dominic Waithe. \n"
	info += "Automatic detection was used to find the cells in this image.\n"
	info += "For more details: https://github.com/dwaithe/amca \n"
	info += "AMCA version used: "+str(d.amcarepo)+" (search github with this).\n"
	info += "Tiff export: tifffile.py (Christoph Gohlke)\n"
	info += "ROI encoded using functions from: https://github.com/dwaithe/ijpython_roi \n"	
	info += "-----------------------\n"
	info += "Acquisition configuration.\n"
	info += "-----------------------\n"
	info += "Microscope type: "+d.microscope_type+".\n"
	info += "Objective type: "+d.objective_type+".\n"
	info += "Camera type: "+d.camera_type+".\n"
	info += "Lamp type: "+d.lamp_type+".\n"
	info += "Objective magnification: "+str(d.objective_mag)+"x.\n"
	info += "Camera pixel size: "+str(d.cam_pixel_size)+" um (raw pixel size of camera before mag and binning).\n"
	info += "Camera binning factor: "+str(d.cam_binning)+" (hardware binning).\n"
	info += "Digital binning factor: "+str(d.digital_binning)+" (digital binning).\n"
	info += "XY-spacing: "+str(d.voxel_xy)+" um, Z-spacing: "+str(d.z_stage_move)+" um.\n"	
	info += "Excitation lines: "+",".join(d.excitation_lines[0:d.ch_to_image])+". \n"
	info += "Camera gain: "+str(d.cam_gain)+"\n"
	s = [str(i) for i in d.exposures[0:d.ch_to_image]] 
	info += "Camera exposures: "+",(ms) ".join(s)+ "ms (acquisition exposure duration).\n"
	info += "Channels imaged: "+str(d.ch_to_image)+" (number of channels imaged).\n"
	info += "Channels analyzed: "+str(d.ch_to_analyze)+" (number of channels on which detection was run).\n"
	info += "-----------------------\n"
	info += "Detection algorithm configuration. \n"
	info += "-----------------------\n"
	info += "Computer name: "+str(d.computer_name)+".\n"
	info += "Processor type: "+str(d.processor_type)+".\n"
	info += "Detection algorithm: "+str(d.algorithm_name)+".\n"
	info += "Detection repo hash: "+d.dkrepo+" (search github with this).\n"
	info += "Detection model configuration: "+str(d.config_path)+".\n"
	info += "Detection model weights: "+str(d.weight_path)+".\n"
	info += "Detection metadata: "+str(d.meta_path)+".\n"
	info += "-----------------------\n"
	info += "Acquisition performed at: "+datetime.now().strftime("%Y/%m/%d, %H:%M:%S") +".\n"
	info += "-----------------------\n"
	info += "Stage X-pos: "+str(d.stage_pos_x)+" um.\n" 
	info += "Stage Y-pos: "+str(d.stage_pos_y)+" um.\n"
	info += "Piezo Z-pos: "
	if d.regions != {}:
		for name in d.regions:
			info += str(name)+", "
	else:
		info += str(d.stage_pos_z)+" um.\n"
	info +=  "(um)\n"
	
	
	resolution = (1./d.voxel_xy,1./d.voxel_xy) #Expects tuple, ratio pixel to physical unit (for unit see 'unit').
	print('numoftimepts',d.num_of_tpts)
	if d.num_of_tpts > 0:
		stp = str(d.tp).zfill(4)
		out_file_path = d.out_path+"img_stk_x_"+str(d.stage_pos_x)+"y_"+str(d.stage_pos_y)+"t_"+stp+".tif"
	else:
		out_file_path = d.out_path+"img_stk_x_"+str(d.stage_pos_x)+"y_"+str(d.stage_pos_y)+".tif"
	
	if not os.path.exists( d.out_path):
    		os.makedirs(d.out_path)	

	tifffile.imsave(out_file_path, im_stk, resolution=resolution, shape=im_stk.shape, ijmetadata={'Overlays':lets_get_meta,'info':info}, metadata=metadata, imagej=True)
	
	
