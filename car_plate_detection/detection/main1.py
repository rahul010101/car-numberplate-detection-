import cv2
import pandas as pd
from ultralytics import YOLO
import numpy as np
import pytesseract
from datetime import date,datetime, timedelta
import os
import re
import shutil
import mysql.connector
import json

source_folder = 'uploads/images'  # Replace with the path to your source folder
destination_folder = 'detection/static/images'  # Replace with the path to your destination folder

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
    json_result_file = "data.json"
    result_file = "results/car_plate_data.txt"
    with open(result_file, "w") as file:
        pass  # Opening the file with "w" mode truncates it (empties it)
    with open(json_result_file, "w") as json_file:
        json_file.write("[]")

    cap = cv2.VideoCapture(file_path)

    my_file = open("./coco1.txt", "r")
    data = my_file.read()
    class_list = data.split("\n")
    count = 0
    area = [(27, 417), (16, 456), (1015, 451), (992, 417)]
    processed_numbers = set()
    frame_count = 0

    while True:
        ret, frame = cap.read()
        count += 1
        if count % 3 != 0:
            continue
        if not ret:
            break

        frame = cv2.resize(frame, (1020, 500))
        results = model.predict(frame)
        a = results[0].boxes.data
        px = pd.DataFrame(a.cpu().numpy()).astype("float")
        numberplate_database()

        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]
            cx = int(x1 + x2) // 2
            cy = int(y1 + y2) // 2
            result = cv2.pointPolygonTest(np.array(area, np.int32), ((cx, cy)), False)
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
                    
                    json_db=f"{text}.json"
                    frame_filename = f"uploads/images/frame_{frame_count}.jpg"
                    cv2.imwrite(frame_filename, frame)
                    frame_count += 1
                    processed_numbers.add(text)

                    # Get video timestamp in milliseconds
                    video_timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)

                    # Convert timestamp to hours, minutes, seconds
                    video_time = str(timedelta(milliseconds=video_timestamp_ms))
                    with open(result_file, "a") as file:
                        file.write(f"{text}\t{video_time}\n")
                    insert_data(text,frame_filename,json_db,video_time)

    
    
    
    move_images(source_folder, destination_folder)
    cap.release()

def move_images(source_folder, destination_folder):

    clean_folder(destination_folder)
    # Create destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Loop through all files in the source folder
    for filename in os.listdir(source_folder):
        # Construct full file path
        file_path = os.path.join(source_folder, filename)

        # Check if it's a file and if it has an image extension
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # Move the file to the destination folder
            shutil.move(file_path, destination_folder)
            print(f"Moved: {filename}")
        else:
            print(f"Skipped: {filename} (not an image)")

def clean_folder(folder):
    # Check if the folder exists
    if os.path.exists(folder):
        # Remove all files in the folder
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove a directory
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        os.makedirs(folder)  # Create the folder if it doesn't exist

def numberplate_database():
    # Establish a connection to the MySQL database
    db_connection = mysql.connector.connect(
        host="localhost",       # or the database server IP address
        user="root",            # MySQL username
        password="",            # MySQL password
        database="number_plate" # Database name
    )

    # Create a cursor object to interact with the database
    cursor = db_connection.cursor(dictionary=True)  # 'dictionary=True' fetches results as dictionaries

    # Write a SQL query to fetch data
    query = "SELECT * FROM number_plate"

    # Execute the query
    cursor.execute(query)

    # Fetch all rows and get column names as keys with data as values
    result = cursor.fetchall()

    # Function to convert date/datetime objects to string
    def convert_dates_to_string(row):
        for key, value in row.items():
            if isinstance(value, (date, datetime)):  # Check if the value is a date or datetime
                row[key] = value.isoformat()  # Convert to string in ISO format
        return row

    # Loop through each row and create individual JSON files
    for row in result:
        # Convert any date or datetime objects to string
        row = convert_dates_to_string(row)

        # Extract the number plate to use as the filename
        plate_number = row.get("plate_number", "unknown").replace(" ", "_")  # Use "unknown" if no plate number exists

        # Create the JSON file for this row, named by the car's number plate
        filename = f"{plate_number}.json"

        # Write the row data to the individual JSON file
        with open(filename, 'w') as json_file:
            json.dump(row, json_file, indent=5)

        print(f"Data for {plate_number} written to {filename}")

    # Close the cursor and the database connection
    cursor.close()
    db_connection.close()

    print("All data successfully written to individual JSON files.")

def insert_data(number_plate, image_path, json_data, timestamp):
    # Establish a connection to the MySQL database
    #timestampstr = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    db_connection = mysql.connector.connect(
        host="localhost",       # or the database server IP address
        user="root",            # MySQL username
        password="",            # MySQL password
        database="number_plate" # Database name
    )
    
    # Create a cursor object to interact with the database
    cursor = db_connection.cursor()

    # Read the image file in binary mode
    with open(image_path, 'rb') as file:
        image_data = file.read()

    # Convert the JSON data into a string format
    json_dict={}
    with open(json_data,'r') as file:
        json_dict=json.load(file)
    
    json_data_str = json.dumps(json_dict)
    print(json_data_str)
    
    # Define the SQL query to insert the data
    query = """
    INSERT INTO detect_num_plates 
    (number_plate_number, time_stamp, image, number_json) 
    VALUES (%s, %s, %s, %s)
    """
    
    # Values to insert into the database
    values = (number_plate, timestamp, image_data, json_data_str)

    # Execute the query and commit the transaction
    cursor.execute(query, values)
    db_connection.commit()
    
    # Close the cursor and the database connection
    cursor.close()
    db_connection.close()

    print("Data successfully inserted into the table.")