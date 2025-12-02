# S2 - MPEG4 and More Endpoints

## Big Buck Bunny Video Processor
A Flask web application that provides 7 endpoints for video processing using FFmpeg

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <https://github.com/mariasannino/audio-and-video-coding-techniques.git>
cd seminar2
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install Flask
```

### 4. Install FFmpeg (if not already installed)
- **macOS:** `brew install ffmpeg`
- **Ubuntu:** `sudo apt install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/)

### 5. Download Big Buck Bunny Video (NOT on GitHub)
```bash
curl -o big_buck_bunny.mp4 https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4
```

**Important:** The video file is in `.gitignore`  will NOT be uploaded to GitHub.

### 6. Run the Application
```bash
python app.py
```

Open your browser to: [http://localhost:5000](http://localhost:5000)

## 7 Tasks / Endpoints

### Task 1: Modify Video Resolution
**Endpoint:** `/task1/<width>/<height>`
- **Example:** `/task1/640/480`
- **Description:** Changes video resolution to specified dimensions
- **Output:** Creates `task1_640x480_full.mp4`

### Task 2: Modify Chroma Subsampling
**Endpoint:** `/task2/<subsampling>`
- **Options:** `420` (4:2:0), `422` (4:2:2), `444` (4:4:4)
- **Example:** `/task2/420`
- **Description:** Changes chroma subsampling format
- **Output:** Creates `task2_420_full.mp4`

### Task 3: Read Video Information
**Endpoint:** `/task3`
- **Description:** Extracts and displays at least 5 relevant data points from the video
- **Output:** HTML page with video information including:
  - Duration
  - File size
  - Bitrate
  - Resolution
  - Codec

### Task 4: Create New Container (20 Seconds - REQUIRED)
**Endpoint:** `/task4`
- **Description:** Creates a new BBB container with multiple audio tracks
- **Requirements from PDF:**
  1. Cut BBB into 20 seconds only video 
  2. Export BBB(20s) audio as AAC mono track 
  3. Export BBB(20s) audio in MP3 stereo w/ lower bitrate (96k) 
  4. Export BBB(20s) audio in AC3 codec 
  5. Package everything in a .mp4 with FFMPEG 
- **Output:** Creates `task4_container_20s.mp4`


### Task 5: Count Tracks in MP4 Container
**Endpoint:** `/task5`
- **Description:** Counts and displays the number of tracks in the MP4 container
- **Output:** Shows video, audio, and subtitle track counts
- **Example Output:** Video: 1, Audio: 1, Subtitle: 0, Total: 2

### Task 6: Show Macroblocks and Motion Vectors
**Endpoint:** `/task6`
- **Description:** Creates a video visualization showing macroblocks and motion vectors. Uses FFmpeg's `codecview` filter with `mv=pf+bf+bb`
- **Output:** Creates `task6_macroblocks_full.mp4`

### Task 7: Show YUV Histogram
**Endpoint:** `/task7`
- **Description:** Creates a video with YUV histogram overlay. Uses FFmpeg's `histogram` filter
- **Output:** Creates `task7_yuv_histogram_full.mp4`

## Project Structure

```
seminar2/
├── app.py                    # Main Flask application with all 7 endpoints
├── requirements.txt          # Python dependencies (Flask only)
├── README.md                 # This file
├── .gitignore               # Excludes video files and temporary outputs
└── venv/                    # Virtual environment (not committed)
```

## Important Notes


### File Sizes
- Original video: ~151 MB (stored locally only)
- Output files: Created temporarily during testing
- No video files are committed to GitHub repository

### Testing
All endpoints can be tested by:
1. Running the Flask app: `python app.py`
2. Opening browser to: `http://localhost:5000`
3. Clicking on the task links






