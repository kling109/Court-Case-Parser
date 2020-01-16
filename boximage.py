# Parses the text once it has been extracted from the image.

# import the necessary packages
from imutils.object_detection import non_max_suppression
import numpy as np
import time
import cv2
import pytesseract

DIM_H = 960
DIM_W = 1280
MIN_CONF = 0.3
OVERLAP = 0.3
PAD = 0.2
PATH = "HireRightImages/wisconsin.png"

# construct the argument parser and parse the arguments
def findTextBoxes(path_to_image):
    # Load the image
    image = cv2.imread(path_to_image)
    original = image.copy()
    (h_orig, w_orig) = image.shape[:2]

    # Set a new height and width as multiples of 32
    (h_new, w_new) = (DIM_H, DIM_W)
    ratio_H = h_orig / float(h_new)
    ratio_W = w_orig / float(w_new)

    # Resize the image
    image = cv2.resize(image, (w_new, h_new))
    (h, w) = image.shape[:2]

    # Set OpenCv to use sigmoid activation and a rectangular box
    # with concatination
    layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]

    # Load the EAST text detector
    print("[ALERT] Loading the EAST text detector..")
    net = cv2.dnn.readNet("frozen_east_text_detection.pb")

    # constuct a blob of the image
    blob = cv2.dnn.blobFromImage(image, 1.0, (w, h), (123.68, 116.78, 103.94), swapRB=True, crop=False)
    start = time.time()
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)
    end = time.time()
    print("[ALERT] Blob construction took {:.6f} seconds".format(end-start))

    # Get rows and columns, then start building bounding boxes.
    (numRows, numCols) = scores.shape[2:4]
    # Boxes are (x,y) coordinates
    boxes = []
    # Confindences are probabilities
    confidences = []
    # Building the boxes
    for y in range(0, numRows):
        # Get properties, then geometrical data for bounding boxes
        scoresData = scores[0, 0, y]
        # Each xData corresponds to a point for the corner of a rectangle
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        for x in range(0, numCols):
            # filter for low confidence
            if scoresData[x] > MIN_CONF:
                # Find offset factor
                (offsetX, offsetY) = (x * 4.0, y * 4.0)

                # Extract rotation angle
                angle = anglesData[x]
                cos = np.cos(angle)
                sin = np.sin(angle)

                # Find height and width with geometry
                h = xData0[x] + xData2[x]
                w = xData1[x] + xData3[x]

                # Find Start and end box coordinates
                endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
                endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
                startX = int(endX - w)
                startY = int(endY - h)

                # Add bounding box and probability
                boxes.append((startX, startY, endX, endY))
                confidences.append(scoresData[x])

    # Remove weak boxes
    end_boxes = non_max_suppression(np.array(boxes), probs = confidences, overlapThresh = OVERLAP)
    results = []
    # Loop over boxes
    for (startX, startY, endX, endY) in end_boxes:
        # Scale the boxes
        startX = int(startX * ratio_W)
        startY = int(startY * ratio_H)
        endX = int(endX * ratio_W)
        endY = int(endY * ratio_H)

        # Initialize padding
        dX = int((endX - startX) * PAD)
        dY = int((endY - startY) * PAD)

        # Apply padding
        startX = max(0, startX - dX)
        startY = max(0, startY - dY)
        endX = min(w_orig, endX + (dX * 2))
        endY = min(h_orig, endY + (dY * 2))

        # Get text values
        roi = original[startY:endY, startX:endX]
        config = ("-l eng --oem 1 --psm 7")
        text = pytesseract.image_to_string(roi, config=config)

        # Add to results
        results.append(((startX, startY, endX, endY), text))

    # Sort the results by box coordinates.
    results = sorted(results, key=lambda r:r[0][0])

    # Emplace results
    for ((startX, startY, endX, endY), text) in results:
        print("OCR TEXT")
        print("--------")
        print("{}\n".format(text))

        # Format text for printing
        text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
        output = original.copy()
        cv2.rectangle(output, (startX, startY), (endX, endY), (0, 255, 0), 2)
        cv2.putText(output, text, (startX, startY - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        # Show the image
        cv2.imshow("Text Detection", output)
        cv2.waitKey(0)

if __name__ == "__main__":
    findTextBoxes(PATH)
