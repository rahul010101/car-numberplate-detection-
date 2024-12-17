# Vehicle Number Plate Detection System 🚗

This project is a **Vehicle Number Plate Detection System** that allows users to upload video files, processes the video to detect car number plates, and fetches detailed vehicle information from an external API. It also displays the extracted information in a user-friendly card layout on a web page.

---

## Table of Contents 📖
1. [Overview](#overview)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Installation and Setup](#installation-and-setup)
5. [Usage](#usage)
6. [File Structure](#file-structure)
7. [Screenshots](#screenshots)
8. [Future Improvements](#future-improvements)
9. [Contributions](#contributions)
10. [License](#license)

---

## Overview 📋

The Vehicle Number Plate Detection System performs the following tasks:
1. Accepts video input through a web interface.
2. Processes the video to detect car number plates using computer vision.
3. Fetches vehicle information for the detected number plates from an external JSON API.
4. Displays the detected plates, timestamps, and vehicle information on a dynamic webpage in card format.

---

## Features 🌟
- **Video Upload**: Users can upload video files through a simple interface.
- **Number Plate Detection**: Detects car number plates from uploaded videos.
- **API Integration**: Fetches vehicle information such as owner details, registration date, vehicle model, and insurance validity from an external JSON API.
- **Dynamic Cards**: Displays results in a structured card layout with images, timestamps, and vehicle details.
- **Error Handling**: Handles missing or invalid data gracefully.

---

## Technologies Used 🛠️

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Computer Vision**: OpenCV
- **Data Handling**: JSON Parsing
- **Storage**: Local file storage for uploads
- **External APIs**: Vehicle information retrieval
- **Static Files**: Django's static file management for images and styles

---

## Installation and Setup 🚀

Follow these steps to set up the project on your local machine:

### Prerequisites
- Python 3.8+ installed
- Django installed
- OpenCV library installed
- A virtual environment (recommended)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/vehicle-number-plate-detection.git
   cd vehicle-number-plate-detection
2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
4. **Run Migrations**:
   ```bash
   python manage.py migrate
5. **Start the Development Server**:
   ```bash
   python manage.py runserver
6. **Upload and Process Videos**:
   Open your browser and go to http://127.0.0.1:8000/ to access the application.

**Usage** 🖥️
1. Visit the Home Page where you can upload a video file.
2. Click Upload to process the video.
3. The application processes the uploaded video and extracts car number plates.
4. Results are displayed on the Result Page with:
5. Detected number plates
6. Date and time of detection
7. Vehicle details fetched from the external API
8. Images of detected frames
9. Explore results in an easy-to-read card layout.
10. File Structure 📂

**Here’s an overview of the main files and directories in this project**:
1.  vehicle-number-plate-detection/
2.  │
3.  ├── uploads/                     # Directory for uploaded video files
4.  ├── results/                     # Results (car_plate_data.txt, JSON files)
5.  ├── static/
6.  │   ├── images/                  # Images for detected frames
7.  │   ├── styles1.css              # CSS file for styling
8.  │
9.  ├── templates/
10. │   ├── index.html               # Video upload page
11. ├── result.html              # Results display page
12. │   ├── detected_plates.html     # Card layout for number plate details
13. │
14. ├── myapp/
15. │   ├── views.py                 # Core logic for video processing and data display
16. │   ├── main1.py                 # Video processing with OpenCV
17. │
18. ├── requirements.txt             # Python dependencies
19. ├── manage.py                    # Django management file
20. └── README.md                    # Project documentation (this file)

**Future Improvements** 🛠️
Real-Time Detection: Integrate live camera feeds for real-time plate detection.
Cloud Integration: Store results and videos in cloud storage (AWS S3, GCP, etc.).
API Enhancements: Use a live vehicle information API for up-to-date data.
Improved UI: Add animations, filters, and search functionality on the results page.
Contributions 🤝
Contributions are welcome! Here's how you can help:

Fork the repository.
Create a feature branch: git checkout -b my-new-feature.
Commit your changes: git commit -am 'Add some feature'.
Push to the branch: git push origin my-new-feature.
Submit a pull request.
License 📄
This project is licensed under the MIT License. You are free to use, modify, and distribute it.

Contact 📧
If you have any questions or feedback, feel free to reach out:

Email: rahul2472001@gmail.com
Happy Coding! 🚀
