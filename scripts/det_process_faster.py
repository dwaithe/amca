#!/usr/bin/env python

# --------------------------------------------------------
# Tensorflow Faster R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Xinlei Chen, based on code from Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.

Some additions by Dominic Waithe 2017.
Manually allow use using additional classes.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from lib.config import config as cfg
from lib.utils.nms_wrapper import nms
from lib.utils.test import im_detect
#from nets.resnet_v1 import resnetv1
from lib.nets.vgg16 import vgg16
from lib.utils.timer import Timer

import tifffile as tifffile




def vis_detections(im, class_name, dets,thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(im, aspect='equal',vmin=0,vmax=255)
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor='red', linewidth=1)
        )
        ax.text(bbox[0], bbox[1] - 2,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor='blue', alpha=0.5),
                fontsize=6, color='white')
        #out_str = class_name+"\t"+str(score)+"\t"+str(bbox[0])+"\t"+str(bbox[1])+"\t"+str(bbox[2])+"\t"+str(bbox[3])+"\n"
        #save_file.write(out_str)

    ax.set_title(('{} detections with '
                  'p({} | box) >= {:.1f}').format(class_name, class_name,
                                                  thresh),
                 fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.draw()


def predict(sess, net, im, image_name,out_path):
    #im, im_ref,im_path
    """Detect object classes in an image using pre-computed object proposals."""
    #path_to_imgs = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/acquisitions/zstacks/test3/pos1_resize/"
    # Load the demo image
    #im_file = os.path.join(cfg.FLAGS2["data_dir"], path_to_imgs, image_name)
    #print(im_file)
    #im = cv2.imread(im_file)
    

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
    print('Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0]))

    # Visualize detections for each class
    CONF_THRESH = 0.7
    NMS_THRESH = 0.7
    out_name = os.path.join(cfg.FLAGS2["data_dir"], out_path, str(image_name)+str('.txt'))
    f =  open(out_name,'w')
    for cls_ind, cls in enumerate(cfg.FLAGS2["CLASSES"][1:]):
        cls_ind += 1  # because we skipped background
        cls_boxes = boxes[:, 4 * cls_ind:4 * (cls_ind + 1)]
        
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes, cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        inds = np.where(dets[:, -1] >= CONF_THRESH)[0]
        
        if len(inds) > 0:
        
            for i in inds:
                bbox = dets[i, :4]
                score = dets[i, -1]
                out_str = cls+"\t"+str(score)+"\t"+str(bbox[0])+"\t"+str(bbox[1])+"\t"+str(bbox[2])+"\t"+str(bbox[3])+"\n"
                f.write(out_str)
        
        #vis_detections(im, cls, dets, thresh=CONF_THRESH)
    f.close()
def start_import(imgstack,demonet,tfmodel):
    # set config
    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth = True
    # init session
    sess = tf.Session(config=tfconfig)
    # load network
    #if demonet == 'vgg16' or 'voc_2007_trainval+test':
    net = vgg16(batch_size=1)
    # elif demonet == 'res101':
        # net = resnetv1(batch_size=1, num_layers=101)
    #else:
    #    raise NotImplementedError
    net.create_architecture(sess, "TEST", cfg.FLAGS2["CLASSES"].__len__(),tag='default', anchor_scales=[8, 16, 32])
    saver = tf.train.Saver()
    saver.restore(sess, tfmodel)

    print('Loaded network {:s}'.format(tfmodel))
    print('opening file: ',imgstack)
    im_stack = tifffile.TiffFile(imgstack).asarray()
    im_path =  os.path.dirname(os.path.abspath(imgstack))
    out_path = imgstack[:-4]
    os.makedirs(out_path, exist_ok=True)

    

    print('shape of stack: ',im_stack.shape)
    for im_ref in range(0,im_stack.shape[0]):
        im_gray = im_stack[im_ref,:,:]
        im = np.zeros((*im_gray.shape,3))
        im[:,:,0] = im_gray
        im[:,:,1] = im_gray
        im[:,:,2] = im_gray
        #im = im.astype(np.uint8)
        im = im.astype(np.float32)
        
        im = im /np.max(im)
        im = im*255.0
        im = im.astype(np.uint8)
        im = im[::2,::2]
        
        predict(sess, net, im , im_ref,out_path)
    #plt.show()

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16 res101]',
                        choices=NETS.keys(), default='res101')
    parser.add_argument('--imgstack', dest='imgstack', help='Trained dataset [pascal_voc pascal_voc_0712]',
                        )
    args = parser.parse_args()

    return args



