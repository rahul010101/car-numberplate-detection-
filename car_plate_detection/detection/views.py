from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
import os
from .main1 import process_video
from django.conf import settings
from django.conf.urls.static import static
import base64
import mysql.connector
import json

def index(request):
    return render(request, 'index.html')

def upload(request):
    if request.method == 'POST' and request.FILES['video']:
        video = request.FILES['video']
        fs = FileSystemStorage(location='uploads')
        filename = fs.save(video.name, video)
        uploaded_file_url = fs.url(filename)

        # Process the uploaded video
        video_path = os.path.join('uploads', filename)
        process_video(video_path)

        return redirect('result')
    return render(request, 'index.html')

def result(request):
    data = []
    try:
        with open('results/car_plate_data.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    data.append(parts)
    except FileNotFoundError:
        data = []

    return render(request, 'result.html', {'results': data})

def detected_plates_view(request):
    # Establish a connection to the MySQL database
    db_connection = mysql.connector.connect(
        host="localhost",       # or the database server IP address
        user="root",            # MySQL username
        password="",            # MySQL password
        database="number_plate" # Database name
    )
    
    # Create a cursor object to interact with the database
    cursor = db_connection.cursor(dictionary=True)

    # SQL query to fetch data from the 'detect_num_plates' table
    query = "SELECT * FROM detect_num_plates"
    cursor.execute(query)
    result = cursor.fetchall()

    # Dynamic array to store the detected data
    detected_data = []


    # Iterate through the fetched data
    for row in result:
        number_json={}
        # Parse the JSON string in the 'number_json' column
        number_json = json.loads(row['number_json'])
          # Convert the JSON back to string format for display
        
        # Assuming the image is stored in the static directory (convert image to an accessible URL path)
        if row['image'] is not None:
            image_base64 = base64.b64encode(row['image']).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{image_base64}"
        else:
            image_url = None
        
        # Check if the 'time_stamp' is None
        if row['time_stamp'] is not None:
            time_str = row['time_stamp']# Convert timestamp to string
        else:
            time_str = "No timestamp available"

        # Append the data to the detected_data list
        detected_data.append({
            'img': image_url,
            'platenumber': row['number_plate_number'],
            'time': time_str,
            'detail': number_json
        })

    # Close the cursor and the database connection
    cursor.close()
    db_connection.close()

    # Pass the dynamic data to the template
    return render(request, 'detected_plates.html', {'detected_data': detected_data})

def car_details(request, plate_number):
    # Establish a connection to the MySQL database
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="number_plate"
    )

    cursor = db_connection.cursor(dictionary=True)

    # Fetch the car details based on the plate number
    query = "SELECT * FROM detect_num_plates WHERE number_plate_number = %s"
    cursor.execute(query, (plate_number,))
    car_data = cursor.fetchone()
    number_json={}
        
    number_json = json.loads(car_data['number_json'])
    
    cursor.close()
    db_connection.close()

    # If car data is found, render the details page
    if car_data:
        image_base64 = base64.b64encode(car_data['image']).decode('utf-8') if car_data['image'] else None
        car_data['img'] = f"data:image/jpeg;base64,{image_base64}" if image_base64 else None

        return render(request, 'car_details.html', {'car': car_data,'number_json':number_json})
    else:
        return render(request, 'car_details.html', {'error': 'Car details not found'})



# def detected_plates_view(request):
#     # Sample data for demonstration
#     data = []
#     try:
#         with open('results/car_plate_data.txt', 'r') as file:
#             lines = file.readlines()
#             for line in lines:
#                 parts = line.strip().split('\t')
#                 if len(parts) == 3:
#                     data.append(parts)
#     except FileNotFoundError:
#         data = []
#     detected_plates = [
#         {
#             'image_url': "/static/images/frame_0.jpg",  # path to image in static folder
#             'details': "Detected at Location A, Date: 01/10/2024, Time: 12:30 PM"
#         },
#         {
#             'image_url': "/static/images/frame_1.jpg",  # path to image in static folder
#             'details': "Detected at Location B, Date: 02/10/2024, Time: 02:45 PM"
#         },
#         {
#             'image_url': "/static/images/frame_2.jpg",  # path to image in static folder
#             'details': "Detected at Location B, Date: 02/10/2024, Time: 02:45 PM"
#         },
#         {
#             'image_url': "/static/images/frame_3.jpg",  # path to image in static folder
#             'details': "Detected at Location B, Date: 02/10/2024, Time: 02:45 PM"
#         }
#     ]
#     zipped_data = zip(detected_plates, data)
    
#     return render(request, 'detected_plates.html', {'zipped_data': zipped_data})
