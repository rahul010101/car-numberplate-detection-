import cv2
import pandas as pd
from ultralytics import YOLO
import numpy as np
import pytesseract
from datetime import datetime
import os
import re

# Set the path to Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load the YOLO model
model = YOLO('./best.pt')

def correct_plate_format(text):
    """
    Correct common OCR mistakes based on typical license plate formats.
    """
    text = text.upper()

    # Replace specific known misreads
    text = text.replace("O", "0", 1)  # Replace O with 0 only for the first occurrence after digits
    text = re.sub(r"(?<=[A-Z])0", "O", text)  # Replace 0 with O if it follows a letter
    text = text.replace("U", "J", 1)  # Replace U with J only for the first occurrence after letters
    text = re.sub(r"(?<=[A-Z])U", "J", text)  # Replace U with J if it follows a letter

    # Keep only alphanumeric characters
    text = re.sub(r'[^A-Z0-9]', '', text)

    # Ensure text matches typical plate formats
    if len(text) < 6 or len(text) > 10:  # Adjust according to your plate format
        return ""

    return text

def process_video(file_path):

    result_file = "results/car_plate_data.txt"
    os.makedirs("results", exist_ok=True)
    with open(result_file, "w") as file:
        pass  # Opening the file with "w" mode truncates it (empties it)

    cap = cv2.VideoCapture(0)
    
    with open("./coco1.txt", "r") as my_file:
        data = my_file.read()
    class_list = data.split("\n") 
    
    # Define the area for detection
    area = [(27, 417), (16, 456), (1015, 451), (992, 417)]
    processed_numbers = set()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image. Exiting...")
            break
        
        frame = cv2.resize(frame, (1020, 500))
        
        # Draw the dark blue rectangle indicating the area
        cv2.polylines(frame, [np.array(area, np.int32)], isClosed=True, color=(255, 0, 0), thickness=2)
        
        results = model.predict(frame)
        a = results[0].boxes.data
        px = pd.DataFrame(a.cpu().numpy()).astype("float")
        
        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]
            cx = int(x1 + x2) // 2
            cy = int(y1 + y2) // 2
            
            # Draw rectangle around detected objects
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            result = cv2.pointPolygonTest(np.array(area, np.int32), (cx, cy), False)
            if result >= 0:
                crop = frame[y1:y2, x1:x2]
                
                # Preprocess the cropped image
                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                gray = cv2.bilateralFilter(gray, 10, 20, 20)
                text = pytesseract.image_to_string(gray, config='--psm 8').strip()
                text = text.replace(' ', '')

                # Correct the format based on context
                text = correct_plate_format(text)
                
                if text and text not in processed_numbers:
                    processed_numbers.add(text)
                    current_datetime = datetime.now()
                    date_str = current_datetime.strftime("%Y-%m-%d")
                    time_str = current_datetime.strftime("%H:%M:%S")
                    with open(result_file, "a") as file:
                        file.write(f"{text}\t{date_str}\t{time_str}\n")
        
        # Display the frame with rectangles and detection area
        cv2.imshow('Live Camera', frame)
        
        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

process_video(None)
