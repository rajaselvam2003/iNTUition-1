from cvzone.HandTrackingModule import HandDetector
import cv2
import os
import os.path
import numpy as np
import streamlit as st
from pdf2image import convert_from_path
from flask import Flask, render_template, Response
# from streamlit_webrtc import webrtc_streamer
# import av
from PIL import Image, ImageOps
import time

# Get the Presentation Slides from Streamlit Website

st.markdown("<h1 style='text-align: center;'>iNTUition</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# display an HTML image
# st.markdown("<img src='https://www.example.com/image.jpg' alt='my image' style='width: 300px;'>", unsafe_allow_html=True)

# display an HTML link
# st.markdown("<a href='https://www.example.com'>My Link</a>", unsafe_allow_html=True)

if uploaded_file is not None:

    # First delete previously uploaded files from Presentation Folder
    folder_path = r'C:\Users\Moham\Desktop\DLW-2022\NTU_Hackathon\Presentation'
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                print(f"Deleted {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

        # Then upload fresh file to folder
        with open(os.path.join(r'C:\Users\Moham\Desktop\DLW-2022\NTU_Hackathon\Presentation',
                               uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File saved successfully.")

    # Get name of file
    folder_path = r'C:\Users\Moham\Desktop\DLW-2022\NTU_Hackathon\Presentation'
    file_names = os.listdir(folder_path)
    PDF_Name = file_names[0]

    # find the path of that file to convert
    PDF_path = r'C:/Users/Moham/Desktop/DLW-2022/NTU_Hackathon/Presentation/' + PDF_Name
    images = convert_from_path(PDF_path)
    Present_Images_Folder = r'C:\Users\Moham\Desktop\DLW-2022\NTU_Hackathon\Presentation'
    # Save each PNG image with a numbered filename
    for i, image in enumerate(images):
        image.save(os.path.join(Present_Images_Folder, f'{i + 1}.png'))

    # Parameters
    width, height = 1280, 720
    gestureThreshold = 300
    folderPath = r'C:\Users\Moham\Desktop\DLW-2022\NTU_Hackathon\Presentation'

    # Camera Setup
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)

    # Hand Detector
    detectorHand = HandDetector(detectionCon=0.6, maxHands=1)

    # Variables
    imgList = []
    delay = 30
    buttonPressed = False
    counter = 0
    drawMode = False
    imgNumber = 0
    delayCounter = 0
    annotations = [[]]
    annotationNumber = -1
    annotationStart = False
    hs, ws = int(120 * 1), int(213 * 1)  # width and height of small image

    # Get list of presentation images
    pathImages = sorted(os.listdir(folderPath), key=len)
    print(pathImages)

    if len(os.listdir(Present_Images_Folder)) == 0:
        print(f"The folder '{folder_path}' is empty")

    else:
        with st.empty():
            while True:
                # Get image frame
                success, img = cap.read()
                img = cv2.flip(img, 1)
                pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
                imgCurrent = cv2.imread(pathFullImage)
                showImg = False

                # Find the hand and its landmarks
                hands, img = detectorHand.findHands(img)  # with draw
                # Draw Gesture Threshold line
                cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

                if hands and buttonPressed is False:  # If hand is detected

                    hand = hands[0]
                    cx, cy = hand["center"]
                    lmList = hand["lmList"]  # List of 21 Landmark points
                    fingers = detectorHand.fingersUp(hand)  # List of which fingers are up

                    # Constrain values for easier drawing
                    xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
                    yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
                    indexFinger = xVal, yVal

                    if cy <= gestureThreshold:  # If hand is at the height of the face
                        if fingers == [1, 0, 0, 0, 0]:
                            print("Left")
                            buttonPressed = True
                            if imgNumber > 0:
                                imgNumber -= 1
                                annotations = [[]]
                                annotationNumber = -1
                                annotationStart = False
                                showImg = True
                        if fingers == [0, 0, 0, 0, 1]:
                            print("Right")
                            buttonPressed = True
                            if imgNumber < len(pathImages) - 1:
                                imgNumber += 1
                                annotations = [[]]
                                annotationNumber = -1
                                annotationStart = False
                                showImg = True

                    if fingers == [0, 1, 1, 0, 0]:
                        cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
                        showImg = True

                    if fingers == [0, 1, 0, 0, 0]:
                        if annotationStart is False:
                            annotationStart = True
                            annotationNumber += 1
                            annotations.append([])
                        print(annotationNumber)
                        annotations[annotationNumber].append(indexFinger)
                        cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
                        showImg = True

                    else:
                        annotationStart = False

                    if fingers == [0, 1, 1, 1, 0]:
                        if annotations:
                            annotations.pop(-1)
                            annotationNumber -= 1
                            buttonPressed = True
                            showImg = True

                else:
                    annotationStart = False

                if buttonPressed:
                    counter += 1
                    if counter > delay:
                        counter = 0
                        buttonPressed = False

                for i, annotation in enumerate(annotations):
                    for j in range(len(annotation)):
                        if j != 0:
                            cv2.line(imgCurrent, annotation[j - 1], annotation[j], (0, 0, 200), 12)

                imgSmall = cv2.resize(img, (ws, hs))
                h, w, _ = imgCurrent.shape
                imgCurrent[0:hs, w - ws: w] = imgSmall

                cv2.imshow("Slides", imgCurrent)
                cv2.imshow("Image", img)

                # if showImg:
                # placeholder = st.empty()
                # placeholder.image(imgCurrent, channels="BGR")
                # with placeholder.container():

                st.image(imgCurrent, channels="BGR")
                imgCurrent = cv2.cvtColor(imgCurrent, cv2.COLOR_RGB2BGR)
                showImg = False

                # for seconds in range(60):
                #    st.write(f"⏳ {seconds} seconds have passed")
                #    time.sleep(1)
                # st.write("✔️ 1 minute over!")
                # placeholder.empty()

                key = cv2.waitKey(1)
                if key == ord('q'):
                    break