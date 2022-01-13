import cv2
import time
import numpy as np
import HandTrackingModule as htm        #using Murtaza Hassan's Hand Tracing Module: https://www.computervision.zone
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pynput.keyboard import Key, Controller

keyboard = Controller()

#keyboard.press('a')
#keyboard.release('a')


################################
wCam, hCam = 640, 480
################################

cap = cv2.VideoCapture(0)   #0 laptop/default 1 webcam
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)


##volume setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (3, 227, 252)
##volume setup


while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:

        # Filter based on size
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        #print("area is" , area)
        if 100 < area < 1000:               #%make sure hand is close to pad

            # Find Distance between index and Thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)
            # print(length)

            # Convert Volume
            volBar = np.interp(length, [50, 200], [400, 150])
            volPer = np.interp(length, [50, 200], [0, 100])

            # Reduce Resolution to make it smoother
            smoothness = 10
            volPer = smoothness * round(volPer / smoothness)

            # Check fingers up
            fingers = detector.fingersUp()
            #print(fingers)

            #skip song gesture
            # Find Distance between index and middle
            lengthP, img, lineInfo = detector.findDistanceBasic(8, 12, img)

            #pause song gesture
            # Find Distance between ring thumb
            lengthT, img, lineInfo = detector.findDistanceBasic(4, 16, img)



        if lengthP < 40:    #pinch with index+thumb to pause/play
               print("do pause song")
               print(lengthP)
               keyboard.press(Key.media_play_pause)
               keyboard.release(Key.media_play_pause)
               time.sleep(3)

        if lengthT < 40:        #pinch with ring+thumb to skip song
                print(lengthT)
                print("skip song \n")
                keyboard.press(Key.media_next)
                keyboard.release(Key.media_next)
                time.sleep(1)


        #volume manipulation
    # If pinky is down set volume
        if not fingers[4]:
            volume.SetMasterVolumeLevelScalar(volPer / 100, None)
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
            colorVol = (0, 255, 0)
            time.sleep(3)
        else:
            colorVol = (255, 0, 0)


    cv2.rectangle(img, (50, 150), (85, 400), (250, 150, 3), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (250, 150, 3), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
##MurtazasWorkshop^

    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'Vol Set at: {int(cVol)}', (380, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, colorVol, 3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_PLAIN,
                4, (52, 204, 235), 3)

    cv2.imshow("Img", img)
    cv2.waitKey(1)