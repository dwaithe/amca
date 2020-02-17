from pyvcam import pvc
from pyvcam.camera import Camera
import matplotlib.pylab as plt
from matplotlib.colors import LinearSegmentedColormap

import numpy as np
import time
###
### ------------------------Photometrics Prime and CoolLED multi-colour capture script-------------------
### by Dominic Waithe 
###
### The CoolLED is connected to the Photometrics Prime CMOS using the BNC cable. The cable labelled 
### "EXPOSE OUT 01" is connected to the GLOBAL TTL input of the CoolLED pE-300 Ultra. No other BNC cables 
### are connected to the Light source for this script to work.
### The CoolLED is set "ON" in "Sequence Runner" Mode, with three channels primed (but not powered).
### Sequence mode means a single BNC can trigger the light sources in sequence.
### The order of the illumination is defined using the CoolLED control POD as is the intensity.
###
cdict1 = {'red':   ((0.0, 0.0, 0.0),
                   (1.0, 1.0, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0))
        }
cdict2 = {'red':   ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.0, 0.0),
                   (1.0, 1.0, 1.0))
        }
cdict3 = {'red':   ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'green': ((0.0, 0.0, 0.0),
                   (1.0, 1.0, 1.0)),

         'blue':  ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0))
        }
red1 = LinearSegmentedColormap('Red1', cdict1)
plt.register_cmap(cmap=red1)
blue1 = LinearSegmentedColormap('Blue1', cdict2)
plt.register_cmap(cmap=blue1)
green1 = LinearSegmentedColormap('Green1', cdict3)
plt.register_cmap(cmap=green1)


def main():
    # Initialize PVCAM and find the first available camera.
    pvc.init_pvcam()
    cam = [cam for cam in Camera.detect_camera()][0]
    cam.open()
    cam.gain = 1
    cam.exp_mode ="Timed"
    #cam.update_mode()
    cam.exp_out_mode = 0
    #cam.speed_table_index = 0
    #With the CoolLED pE-300 Ultra in sequence mode, this will cycle through the 3 lamps.
    t0 = time.time()
    frame1= cam.get_frame(exp_time=500) #Exposure channel 1
    frame2= cam.get_frame(exp_time=1000) #Exposure channel 2
    frame3= cam.get_frame(exp_time=500) #Exposure channel 3
    t1 = time.time()
    print(np.round(t1-t0,3),"s to acquire")
    cam.close()
    pvc.uninit_pvcam()
    f, axes = plt.subplots(3, 2)
    axes[0,0].imshow(frame1,cmap=plt.get_cmap('Blue1'))
    axes[0,1].hist(frame1.flatten(),bins=np.arange(0,65535,1000))
    axes[1,0].imshow(frame2,cmap=plt.get_cmap('Green1'))
    axes[1,1].hist(frame2.flatten(),bins=np.arange(0,65535,1000))
    axes[2,0].imshow(frame3,cmap=plt.get_cmap('Red1'))
    axes[2,1].hist(frame3.flatten(),bins=np.arange(0,65535,1000))
    plt.show()

if __name__ == "__main__":
    main()
