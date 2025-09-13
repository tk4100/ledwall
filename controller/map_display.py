#!/usr/bin/env python
import serial
import struct
import time
import cv2
import sys
import os
import pickle

from treecontrol import TreeController
from xmasdata import XmasStrand

def verb(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

def getPhoto(capturedev):
    result = False
    i = 0
    while result == False or i < 5:
        result, frame = capturedev.read()
        if i > 5:
            verb("\nFailed to capture frame!\n")
            return(False)
        i += 1

    frame = cv2.GaussianBlur(frame, (15,15), 0)

    return(frame)

def getDispersion(a, b, c):
    disp = 0
    disp += abs(a[0] - b[0])
    disp += abs(a[1] - b[1])

    disp += abs(b[0] - c[0])
    disp += abs(b[1] - c[1])

    disp += abs(c[0] - a[0])
    disp += abs(c[1] - a[1])

    disp /= 3

    return(disp)

def averagePos(r, g, b):
    x = (r[0] + g[0] + b[0]) / 3
    y = (r[1] + g[1] + b[1]) / 3

    return([x,y])

def captureBench():
    print("!--  BENCHMARK ENABLED --!\n\nNot actually scanning the tree.")
    sample_time = 10
    samples_captured = 0
    test_end = time.time() + sample_time
    while time.time() < test_end:
        bench_photo = getPhoto(cap)
        samples_captured += 1
    samples_per_sec = samples_captured / sample_time
    print(f"Captured {samples_captured} samples, at {samples_per_sec:.02f} samples/sec")
    quit()

###

tree = TreeController(300)
strand = XmasStrand()
strand.wipeDB()

cap = cv2.VideoCapture(0, apiPreference=cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1);
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30)

angle = int(sys.argv[1])

# capture benchmark.  How many frames per second can we capture?
#captureBench()

# calibrate
tree.clear()
calibration = getPhoto(cap)
cal_b,cal_g,cal_r = cv2.split(calibration)
for led in [0] + [x for x in range(0,301)]:

    verb(f"LED {led}")

    # get blue photo
    tree.setLed(led, 255, 255, 255)
    photo = getPhoto(cap)
    tree.clear()

    # gen diff for each channel
    blue,_,_ = cv2.split(photo)
    _,green,_ = cv2.split(photo)
    _,_,red = cv2.split(photo)

    diff_r = cv2.subtract(red, cal_r)
    diff_g = cv2.subtract(green, cal_g)
    diff_b = cv2.subtract(blue, cal_b)

    # find bright spot in each diff
    (minVal, maxVal_r, minLoc, maxLoc_r) = cv2.minMaxLoc(diff_r)
    (minVal, maxVal_g, minLoc, maxLoc_g) = cv2.minMaxLoc(diff_g)
    (minVal, maxVal_b, minLoc, maxLoc_b) = cv2.minMaxLoc(diff_b)

    # filter out low-signal images
    image_passed = True
    peak = max([maxVal_r, maxVal_g, maxVal_b])
   
    # filter out poorly corrlated channels
    dispersion = getDispersion(maxLoc_r, maxLoc_g, maxLoc_b)

    # mark for non-inclusion in our dataset
    if peak < 128 or dispersion > 40:
        image_passed = False

    # draw a circle for manual verification
    avg_position = averagePos(maxLoc_r, maxLoc_g, maxLoc_b)
    result = cv2.merge((diff_b,diff_g,diff_r))
    result = cv2.circle(result, maxLoc_r, 13, (0, 0, 255), 2)
    result = cv2.circle(result, maxLoc_g, 16, (0, 255, 0), 2)
    result = cv2.circle(result, maxLoc_b, 19, (255, 0, 0), 2)
    result = cv2.circle(result, [ int(avg_position[0]), int(avg_position[1]) ], 6, (255, 0, 255), 2)

    # burn details into the image
    accuracy_index = peak
    if dispersion > 0:
        accuracy_index /= dispersion
    deets = f"Dispersion: {dispersion:.02f} Peak: {peak:.02f} Accuracy: {accuracy_index:.02f} Include: {image_passed}"
    result = cv2.putText(result, deets, (00,85), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA, False)

    # record!
    if image_passed:
        strand.captureLED(angle, led, avg_position[0], avg_position[1])



    cv2.imwrite(f'images/cal.png', calibration)
    cv2.imwrite(f'images/led_{led}_{angle}deg_result.png', result)
    cv2.imwrite(f'images/og_led_{led}_{angle}deg.png', photo)
   
    verb("\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r                                      \r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r")

print("\nFinished.")
strand.flush()
cap.release()

        
