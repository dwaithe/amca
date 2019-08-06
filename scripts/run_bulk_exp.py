import subprocess

#Global variables
path_to_darknet ="/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/darknet/"
path_to_data = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/"



#Experiment specific.
path_to_init_model = path_to_darknet+"darknet19_448.conv.23"
path_to_training_def = path_to_data+"neuroblastoma_phal_dapi_class/2018/obj_neuroblastoma_phal_dapi_class180.data"
GPU_to_use = 1

foutfile="indflip_colour_on_noncol"
cfg_file="yolo-obj"

#Training.
out = subprocess.call(path_to_darknet+"darknet detector train "+path_to_training_def+" "+path_to_darknet+"cfg/"+cfg_file+".cfg "+path_to_init_model+" -gpus "+str(GPU_to_use), shell=True)

print("finished",out)