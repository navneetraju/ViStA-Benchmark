import numpy as np
import argparse
import imutils
import time
import cv2
import os

def get_large_videotranscription(path_to_video):
    args = {}
    args['yolo']="yolo-coco"
    args['confidence']=0.5
    args['threshold']=0.3
    labelsPath = "yolo-coco/coco.names"
    LABELS = open(labelsPath).read().strip().split("\n")
    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),dtype="uint8")
    weightsPath = "yolo-coco/yolov3.weights"
    configPath = "yolo-coco/yolov3.cfg"
    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    vs = cv2.VideoCapture(path_to_video)
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    if int(major_ver) < 3:
        fps = vs.get(cv2.cv.CV_CAP_PROP_FPS)
        print("[INFO]Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
    else:
        fps=vs.get(cv2.CAP_PROP_FPS)
        print("[INFO]Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
    writer = None
    (W, H) = (None, None)
    try:
        prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT if imutils.is_cv2() \
            else cv2.CAP_PROP_FRAME_COUNT
        total = int(vs.get(prop))
        print("[INFO] {} total frames in video".format(total))
    except:
        print("[INFO] could not determine # of frames in video")
        print("[INFO] no approx. completion time can be provided")
        total = -1
    dic={}
    fps=int(fps)
    count = 0
    while True:
        (grabbed, frame) = vs.read()
        if count%fps != 0:
            count+=1
            continue
        count+=1
        if not grabbed:
            break
        if W is None or H is None:
            (H, W) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        start = time.time()
        layerOutputs = net.forward(ln)
        end = time.time()
        boxes = []
        confidences = []
        classIDs = []
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > args["confidence"]:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
            args["threshold"])
        l=[]
        
        if len(idxs) > 0:
            
            for i in idxs.flatten():
                l.append(LABELS[classIDs[i]])
        print(l)
        for i in l:
            if(i not in dic):
                dic[i]=1
            else:
                dic[i]=dic[i]+1
        print(dic)
        print("[INFO] cleaning up...")
    vs.release()
    return dic
