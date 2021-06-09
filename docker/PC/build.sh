#!/bin/sh
docker build --rm --build-arg USER_ID=$UID -t argnctu/sis_2020:detectron2 .
