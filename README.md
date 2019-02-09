# amca
This is a repository for the Automated Microscopy Control Environment.

There is a biorxiv paper associated with the development of this package. This can be found here:
https://www.biorxiv.org/content/10.1101/544833v1


### Requirements
to make use of this repository some other repositories are required. Please download or clone these repositories into the same folder as AMCA is situtated.
- Faster-RCNN - adapted for microscopy https://github.com/dwaithe/Faster-RCNN-TensorFlow-Python3.5
- YOLOv2 - adapted for microscopy https://github.com/dwaithe/yolov2 (optional)
- YOLOv3 - adapted for microscopy (optional)



### Labview integration. 
For this project we used Labview 2015. 
For this project it was necessary to install the Labview drivers for the Photometrics Prime Camera.
More details for support can be found here: https://www.photometrics.com/resources/third-party-software/labview
This involves installing PVCAM: https://www.photometrics.com/support/software/
The .vi files used for this project can be found in the labview subdirectory of this repository
- amca.vi -- This is the main script used for running the microscope.
- formatDataCallPython.vi -- This a .vi called by amca.vi and interfaces labview with python scripts
- splitAndSum.vi -- This is the .vi called by 'formatDataCallPython.vi' and performs binning of images.
- ExOpenGlobalCam.vi -- This is the script used for opening the camera before acquisition.
- ExCloseGlobalCam.vi -- This is the script used for closing the camera after acquisition.


### SRC
In this subdirectory you will find the main python scripts which I use to perform the imaging.
- collect_positions.py -- This is the script used to generate the list of positions for the microscope to visit.
- amca.py -- This is the python script called by Labview which processes each image as it is acquired by the camera.
- review_on_micro.py -- This allows visualisation of regions using the augmented reality display as you move around the microscopy stage.


### Extra Scripts
In the scripts subdirectory you will find many of the python and IJmacro scripts that I used to make life easier.
Python scripts are written in python 3.5.

- ConvertFromROItoCellVolumes.ipynb -- Development notebook for converting detections into contiguous regions for measurement.
- Faster-RCNN to SORT format.ipynb -- Development notebook for various things.
- format_data_for_graphPad.ipynb -- Helper notebook which converts outputs of Faster-RCNN and YOLO into a format which is compatible with GraphPad, for easy plotting.
- read and generate position lists for darknet.ipynb -- Notebook which contains scripts for converting from VOC format to YOLO format for the annotations.
- simulated slide -- Script which allows you to generate positions 

ImageJ macro scripts


### Augmented Reality Microscope schematic and instructions
For this project we developed an attachment to our Olympus IX73 microscope which meant it could be used for Augmented Reality.

![](augmented_reality_microscope/gif_augmented_reality.gif)


