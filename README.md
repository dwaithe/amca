# AMCA - Automated Microscopy Control Environment.
This is a repository for the Automated Microscopy Control Environment.

There is a biorxiv paper associated with the development of this package. This can be found here:
https://www.biorxiv.org/content/10.1101/544833v2

We run the system using a Nvidia Jetson TX2 development board and use a LattePanda development board to support the control of our microscope. The system would also be compatible with the Nivida Jetson Nano and Javier ranges of computers. If you have access to Python drivers for your hardware then please make sure they are compiled to run on aarch64 Linux, if you use the Jetson system. If drivers are only available for Windows 64-bit then you can use a LattePanda system to accommodate these drivers and communicate with the Jetson via Python sockets. A full '.pdf' guide for this is coming soon. Unless you use exactly the same configuration then some changes will be needed to the scripts to ensure they work with your hardware and computer systems. 

### Hardware requirements. 
- A microscope camera. We use a Photometrics Prime sCMOS camera.  
- An automated XY microscope stage. We used an ASI automated XY stage.  
- An automated Z-piezo (or a XYZ stage). We used a PI Piezo (P-733 2CL).  
- Light-source. We used a CoolLED Ultra pe300 LED light source.  
- An optical microscope. We used a Olympus IX73 microscope with a 100X UPlanSApo, NA 1.4 objective.
.
### Requirements. 
To make use of this repository some other repositories are required. Please download or clone these repositories into the same root folder as AMCA is situated.  You will also need to follow the installation instructions of this different algorithms we require some compilation steps.
Please download one of the following object detection algorithms:  
- YOLOv2 - adapted for microscopy https://github.com/dwaithe/darknet3AB (recommended)
- Faster-RCNN - adapted for microscopy https://github.com/dwaithe/Faster-RCNN-TensorFlow-Python3.5 (optional)
- YOLOv3 - adapted for microscopy https://github.com/dwaithe/darknet3AB (same location as YOLOv2)
- RetinaNet - adapted for microscopy https://github.com/dwaithe/keras-retinanet (optional)

### Scripts for annotation and dataset generation. 
To train the system for your own use please use the scripts contained within the scripts subdirectory. You will find many of the python and ImageJ/FIJI scripts that I used to make this process easier. To create annotations, single channel 2-D images should be acquired at an appropriate optical and digital resolution for your application. Annotations may either be created using the FIJI/ImageJ software [1] or through using an OMERO instance and the webclient [2].
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


### Creating training datasets.   
Python scripts are written in Python 3.5+. If you are new to Python I recommend you install an environment like [Anaconda](https://www.anaconda.com/distribution/) which has everything pre-installed (select the Python 3.# version).
This notebook allows you to import 2-D tiff files with annotation and create JPEG images and XML data corresponding to the annotations:  
[dset01_create_anno_from_TIFF.ipynb](https://github.com/dwaithe/amca/blob/master/scripts/dset01_create_anno_from_TIFF.ipynb).  
This notebook allows you to import from an OMERO server, files and annotations to create a JPEG iamge and XML training dataset:  
[dset01_create_anno_from_omero.ipynb](https://github.com/dwaithe/amca/blob/master/scripts/dset01_create_anno_from_omero.ipynb). 
This notebook contains tools which allow you to convert your JPEG images and XML annotations into full training and testing datasets for use with one of the four object detection algorithms outlined above:  
[dset02_convert_anno_formats.ipynb](https://github.com/dwaithe/amca/blob/master/scripts/dset02_convert_anno_formats.ipynb).  


### Training the object detection algorithm:  
We recommend working with YOLOv2, but a model can be created with any of the above mentioned object detection models. Extensive details can be found through the links provided above. All the necessary files are created for each system in the "creating training datasets" section. We recommend that users perform training on a GPU enabled system. Typically this can be performed in 12 hours with a GPU but performance varies depending on your system. If you do not have access to one locally then I recommend using a cloud based solution for example Microsoft Azure, Amazon Web Service or Google Cloud. Instructions for how to do this are available on request.

For YOLOv2 the process can be summarised as follows:  
- Take your dataset and locate it into a folder (e.g. datasets/C127_dapi_class/2018/).  
- Next navigate to your YOLOv2 folder (we use "/darknet3AB/darknet/")
- Next run the training (e.g. for YOLOv2 as follows, with 1 class in the data):  
```
darknet.exe detector train ../../datasets/C127_dapi_class/2018/obj_c127_dapi_class30.data cfg/yolov2_dk3AB-classes-1-flip.cfg darknet19_448.conv.23
```
This will train the network on the dataset defined in 'obj_c127_dapi_class30.data' using the network configuration defined in 'yolov2_dk3AB-classes-1-flip.cfg'. As a starting point it will use the 'darknet19_448.conv.23' pretrained convolutional network which can be downloaded [here](https://pjreddie.com/media/files/darknet19_448.conv.23).  
- Models trained for different iterations will be exported a key iterations into a folder located in /models/darknet/your_class_name/'.
- The process will terminate after 10000 iterations and a model name suffixed with final will be generated.

### Using AMCA to automate microsopy.  
With a trained model you can now run the main AMCA model. The AMCA algorithm runs in Python and interfacing directly with the hardware of your microscope. The exact operation and configuration will vary with your microscope attachments or equipment. 

In this subdirectory you will find the main python scripts which I use to perform the imaging.
- src/collect_positions.py -- This is the script used to generate the list of positions for the microscope to visit.
- src/amca.py -- This is the python script which runs the dynamic acquisition process.
- src/review_on_micro.py -- This allows visualisation of regions using the augmented reality display as you move around the microscopy stage.

- To run the system you must first generate a positions file ('POS_FILE.txt') using the 'collect_positions.py' script. Run the script and follow the prompts.
- Next, before running the system, it is important to define some inputs and outputs in the "amca.py" file:
```Python
d.out_path = "/media/nvidia/UNTITLED/acquisitions/0001/" #Output folder for image Tiffs generated by microscope.
positions_file_path = "../pos_files/POS_FILE.txt" #Location of positions created by "collect_positions.py".
output_positions_file = "../pos_files/file_pos_export.txt" #output file containg all the positions where cells were located during the experiment.
config_path = "../../darknet3AB/darknet/cfg/yolov2_dk3AB-classes-1-flip.cfg" #The configuration used for training
meta_path =  "../../cell_datasets/c127_dapi_class/2018/obj_c127_dapi_class30.data" #The dataset file definition.
weight_path = "../../models/darknet/c127_dapi_class30/yolov2_dk3AB-classes-1-no-flip_final.weights" #The model created during the training phase.
```
- Now run Python 'amca.py' and watch your microscope automatically recognise and acquire image stacks in the positions outlined in the positions file.

### Post acquisition. 
The AMCA system will generate a ImageJ TIFF stack in each position that the microscope visited and found cells. The ROI of the cells are embedded into each file. These ROI can be accessed through the metadata of the file in Python using the (library)['https://github.com/dwaithe/ijpython_roi'], or can be viewed directly in ImageJ/Fiji simply by opening the file. 

### Augmented Reality Microscope schematic and instructions. 
For this project we developed an attachment to our Olympus IX73 microscope which meant it could be used for Augmented Reality.
This can be activated during the 'amca.py' acquisiton or using the 'review_on_micro.py' subsequently.

![](augmented_reality_microscope/gif_augmented_reality.gif)

[1]http://www.nature.com/nmeth/journal/v9/n7/full/nmeth.2019.html
[2]https://www.nature.com/articles/nmeth.1896

