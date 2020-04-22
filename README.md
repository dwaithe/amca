# amca
This is a repository for the Automated Microscopy Control Environment.

There is a biorxiv paper associated with the development of this package. This can be found here:
https://www.biorxiv.org/content/10.1101/544833v2

We run the system using a Nvidia Jetson TX2 development board and use a LattePanda development board to support the control of our microscope. The system would be also be compatible with the Nivida Jetson Nano and Javier ranges of computers.


### Requirements
To make use of this repository some other repositories are required. Please download or clone these repositories into the same folder as AMCA is situated.  
Please download one of the following object detection algorithms:  
- YOLOv2 - adapted for microscopy https://github.com/dwaithe/yolov2 (recommended)
- Faster-RCNN - adapted for microscopy https://github.com/dwaithe/Faster-RCNN-TensorFlow-Python3.5 (optional)
- YOLOv3 - adapted for microscopy (optional)
- RetinaNet - adapted for microscopy https://github.com/dwaithe/keras-retinanet (optional)


### SRC the main files you will need for performing the acquisiton are the following:
In this subdirectory you will find the main python scripts which I use to perform the imaging.
- collect_positions.py -- This is the script used to generate the list of positions for the microscope to visit.
- amca.py -- This is the python script called by Labview which processes each image as it is acquired by the camera.
- review_on_micro.py -- This allows visualisation of regions using the augmented reality display as you move around the microscopy stage.


### Scripts for annotation and dataset generation
To train the system for your own use please use the scripts contained within the scripts subdirectory. You will find many of the python and ImageJ/FIJI scripts that I used to make this process easier.


Annotation scripts:
To create annotations, single channel 2-D images should be acquired at an appropriate optical and digital resolution for your application. Annotations may either be created using the FIJI/ImageJ software [1] or through using an OMERO instance and the webclient [2].
#### For Fiji/ImageJ the process is as follows:  
- The user should open an image, any bioformats compatible microscopy iamge format is fine.  
- using the "Rectangle" tool, draw around a cell within image to create a Region-Of-Interest (ROI).  
- Add this ROI to the ROI Manager (Analyze->Tools->ROI Manager) and then repeat for each of the cells present in the image.  
- Convert the ROI to Overlays using the "From ROI Manager" command (Image->Overlay->From ROI Manager).  
- Save the image as a 'Tiff' file (File->Save As->Tiff...) into a clearly labelled folder.   
- Repeat for each image in the dataset.  
#### For OMERO the process is as follows:  
- The user should upload their images to the OMERO instance using one of their clients [for more details](https://help.openmicroscopy.org/getting-started-5.html).  Make sure the images are uploaded to a unique dataset in a project of choice.
- Once in OMERO the images can be viewed and annotated using the webclient [for details relating to the webclient](https://help.openmicroscopy.org/web-client.html)
- Double-click and image within the dataset. Click the ROIs tab of the image viewer. Using the "Draw rectangle" tool draw around each cell in an image.
- You may wish to differentally label each ROI with the class of the cell, or label them all with the same class. This bulk naming can also be performed later.
- Make sure to save the Annotations and names to the file using the "Save" button. 
- Repeat for all images in a dataset.


### Creating training datasets:
Python scripts are written in Python 3.5+. If you are new to Python I recommend you install an environment like [Anaconda](https://www.anaconda.com/distribution/) which has everything pre-installed (select the Python 3.# version).
This notebook allows you to import 2-D tiff files with annotation and create JPEG images and XML data corresponding to the annotations:  
[dset01_create_anno_from_TIFF.ipynb](https://github.com/dwaithe/amca/blob/master/scripts/dset01_create_anno_from_TIFF.ipynb).  
This notebook allows you to import from an OMERO server, files and annotations to create a JPEG iamge and XML training dataset:  
[dset01_create_anno_from_omero.ipynb](https://github.com/dwaithe/amca/blob/master/scripts/dset01_create_anno_from_omero.ipynb). 
This notebook contains tools which allow you to convert your JPEG images and XML annotations into full training and testing datasets for use with one of the four object detection algorithms outlined above:  
[dset02_convert_anno_formats.ipynb](https://github.com/dwaithe/amca/blob/master/scripts/dset02_convert_anno_formats.ipynb).  



### Augmented Reality Microscope schematic and instructions
For this project we developed an attachment to our Olympus IX73 microscope which meant it could be used for Augmented Reality.

![](augmented_reality_microscope/gif_augmented_reality.gif)

[1]http://www.nature.com/nmeth/journal/v9/n7/full/nmeth.2019.html
[2]https://www.nature.com/articles/nmeth.1896

