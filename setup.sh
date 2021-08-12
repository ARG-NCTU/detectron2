#!/usr/bin/env bash

roscd rcnn_pkg && cd weigths && python3 download_model.python3

roscd rcnn_pkg && cd datasets && python3 download_brandname_coco.py  

