#!/usr/bin/env python3

import numpy as np
import cv2
import roslib
import rospy
import struct
import math
import time
from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo, CompressedImage
from geometry_msgs.msg import PoseArray, PoseStamped
from visualization_msgs.msg import Marker, MarkerArray
import rospkg
from cv_bridge import CvBridge, CvBridgeError
import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torch.autograd import Variable
import os 
import message_filters

import detectron2
from detectron2.utils.logger import setup_logger

# import some common detectron2 utilities
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.engine import DefaultTrainer
from detectron2 import model_zoo
from detectron2.data.datasets import register_coco_instances

class rcnn_detection(object):
	def __init__(self):
		self.is_compressed = False
		r = rospkg.RosPack()
		self.path = r.get_path('rcnn_pkg')
		self.cv_bridge = CvBridge() 
		self.count = 0

		#### Publisher
		self.image_pub = rospy.Publisher("~predict_img", Image, queue_size = 1)
		self.img_bbox_pub = rospy.Publisher("~predict_bbox", Image, queue_size = 1)
		self.predict_img_pub = rospy.Publisher("/prediction_img", Image, queue_size = 1)
		self.predict_mask_pub = rospy.Publisher("/prediction_mask", Image, queue_size = 1)

		register_coco_instances('brandname_train', {}, 
								'/home/arg/detectron2/datasets/brandname_cocoformat/train/annotations.json', 
							'/home/arg/detectron2/datasets/brandname_cocoformat/train')
		register_coco_instances('brandname_val', {}, 
								'/home/arg/detectron2/datasets/brandname_cocoformat/val/annotations.json', 
							'/home/arg/detectron2/datasets/brandname_cocoformat/val')
		self.subt_metadata = MetadataCatalog.get("brandname_train")
		self.dataset_dicts = DatasetCatalog.get("brandname_train")

		self.cfg = get_cfg()
		self.cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))

		
		self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")  # Let training initialize from model zoo
		self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 22  # datasets classes
		self.cfg.DATALOADER.NUM_WORKERS = 0 #Single thread
		# self.cfg.MODEL.WEIGHTS = os.path.join(self.path, "weights", "model_delta_0011279.pth")
		self.cfg.MODEL.WEIGHTS = os.path.join(self.path, "weights", "model_0003999.pth")
		self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7   # set the testing threshold for this model

		self.predictor = DefaultPredictor(self.cfg)

		### msg filter 
		image_sub = message_filters.Subscriber('/camera/color/image_raw', Image)
		depth_sub = message_filters.Subscriber('/camera/aligned_depth_to_color/image_raw', Image)
		ts = message_filters.TimeSynchronizer([image_sub, depth_sub], 10)
		ts.registerCallback(self.callback)

	def callback(self, img_msg, depth):
		if(self.count % 10 == 0):
			try:
				cv_image = self.cv_bridge.imgmsg_to_cv2(img_msg, "bgr8")
			except CvBridgeError as e:
				print(e)

			outputs = self.predictor(cv_image)	
			v = Visualizer(cv_image[:, :, ::-1],
						metadata=self.subt_metadata, 
						scale=0.8, 
					#	 instance_mode=ColorMode.IMAGE_BW   # remove the colors of unsegmented pixels
			)
			v = v.draw_instance_predictions(outputs["instances"].to("cpu"))
			self.image_pub.publish(self.cv_bridge.cv2_to_imgmsg(v.get_image()[:, :, ::-1], "bgr8"))
			print("Detected 1 frame !!!")

	def onShutdown(self):
		rospy.loginfo("Shutdown.")	
	

if __name__ == '__main__': 
	rospy.init_node('rcnn_detection',anonymous=False)
	rcnn_detection = rcnn_detection()
	rospy.on_shutdown(rcnn_detection.onShutdown)
	rospy.spin()
