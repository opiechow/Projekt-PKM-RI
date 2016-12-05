import cv2
import argparse
import datetime
import time
import numpy as np
import math

meas=[]
pred=[]
enable = True

def analiza():
    global enable
    g_x = 0
    g_y = 0
    g_h = 0
    g_w = 0

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
    args = vars(ap.parse_args())
    camera = cv2.VideoCapture("13.mp4")
    #camera = cv2.VideoCapture(0)
    img = cv2.imread('tory.jpg',cv2.IMREAD_GRAYSCALE)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    fgbg = cv2.createBackgroundSubtractorMOG2()

    time.sleep(2.0)

    frame = np.zeros((400,400,3), np.uint8) # drawing canvas
    mp = np.array((2,1), np.float32) # measurement
    tp = np.zeros((2,1), np.float32) # tracked / prediction

    kalman = cv2.KalmanFilter(4,2)
    kalman.measurementMatrix = np.array([[1,0,0,0],[0,1,0,0]],np.float32)
    kalman.transitionMatrix = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]],np.float32)
    kalman.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32) * 0.03
    #kalman.measurementNoiseCov = np.array([[1,0],[0,1]],np.float32) * 0.00003

    while True:
        (grabbed, frame) = camera.read()

        if not grabbed:
            break

        gray = fgbg.apply(frame)
        gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        _, cnts, _ = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        t_y = 0
        t_x = 0
        t_h = 0
        t_w = 0
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if img[y+h/2, x+w/2] == 0:
                if w > t_w and h > t_h and (w > 50 or h > 50):
                    t_x = x
                    t_y = y
                    t_h = h
                    t_w = w

                img[y+h/2, x+w/2] = 120

        if t_x > 10 or t_y > 10:
            g_x = t_x
            g_y = t_y

        if len(pred) > 1:
            temp_x = pred[-1][0]
            temp_y = pred[-1][1]
            dist1 = math.sqrt(math.pow(math.fabs(temp_x - g_x), 2) + math.pow(math.fabs(temp_y - g_y), 2))

            temp_x = pred[-2][0]
            temp_y = pred[-2][1]
            dist2 = math.sqrt(math.pow(math.fabs(temp_x - g_x), 2) + math.pow(math.fabs(temp_y - g_y), 2))

            if dist1 > 100 or dist2 > 100:
                enable = False

            else:
                enable = True

        kalman.correct(mp)
        tp = kalman.predict()
        if tp[0] != 0 or tp[1] != 0:
            pred.append((int(tp[0]), int(tp[1]), datetime.datetime.now().strftime("%M:%S.%f")))
            #print pred[-1]
            cv2.rectangle(frame, (int(tp[0]), int(tp[1])), (int(tp[0]) + 10, int(tp[1]) + 10), (255, 0, 0), 2)

        mp = np.array([[np.float32(g_x)], [np.float32(g_y)]])
        meas.append((g_x, g_y))


        #cv2.rectangle(frame, (g_x, g_y), (g_x+g_w/2, g_y+g_h/2), (0, 255, 0), 2)


        cv2.imshow("Security Feed", frame)
        #cv2.imshow("test", img)
        #cv2.imshow("gray", gray)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    camera.release()
    analiza()
    return
#analiza()
