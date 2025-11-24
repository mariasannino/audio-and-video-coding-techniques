"""
Image Processing API - Practice 1
FastAPI with image processing endpoints
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import numpy as np
import os
import tempfile
from typing import List, Union

app = FastAPI(title="Image Processing API", version="1.0.0")

# Predefined file paths for simplicity
INPUT_IMAGE = "input_files/input.jpg"
OUTPUT_RESIZED = "output_files/resized.jpg"
OUTPUT_BW = "output_files/bw.jpg"

# Exercise 2: Color Converter
class ColorConverter:
    """Convert between RGB and YUV color spaces"""
    
    def rgb_to_yuv(self, r, g, b):
        y = 0.299 * r + 0.587 * g + 0.114 * b
        u = -0.14713 * r - 0.28886 * g + 0.436 * b
        v = 0.615 * r - 0.51499 * g - 0.10001 * b
        return y, u, v
    
    def yuv_to_rgb(self, y, u, v):
        r = y + 1.140 * (v - 128)
        g = y - 0.395 * (u - 128) - 0.581 * (v - 128)
        b = y + 2.032 * (u - 128)
        return r, g, b

# Exercise 3: Image Resize using Docker FFmpeg
def resize_with_docker(width, height):
    """Resize image using FFmpeg in Docker container"""
    try:
        cmd = [
            'docker', 'exec', 'practice1-ffmpeg-1',
            'ffmpeg', '-y',
            '-i', '/input/input.jpg',
            '-vf', f'scale={width}:{height}',
            '/output/resized.jpg'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        return False

# Exercise 4: Serpentine Reading
def read_serpentine(file_path):
    """Read file bytes in zigzag order"""
    zigzag = [0,1,5,6,14,15,27,28,2,4,7,13,16,26,29,42,3,8,12,17,25,30,41,43,
              9,11,18,24,31,40,44,53,10,19,23,32,39,45,52,54,20,22,33,38,46,51,
              55,60,21,34,37,47,50,56,59,61,35,36,48,49,57,58,62,63]
    
    with open(file_path, 'rb') as f:
        data = f.read()
        return [data[i] for i in zigzag if i < len(data)]

# Exercise 5.1: BW Conversion with Docker FFmpeg
def convert_bw_docker():
    """Convert image to black and white using Docker FFmpeg"""
    try:
        cmd = [
            'docker', 'exec', 'practice1-ffmpeg-1',
            'ffmpeg', '-y',
            '-i', '/input/input.jpg',
            '-vf', 'format=gray',
            '-qscale:v', '31',
            '/output/bw.jpg'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        return False

# Exercise 5.2: Run-Length Encoding
def run_length_encode(data):
    """Compress data using run-length encoding"""
    if not data:
        return []
    
    encoded = []
    count = 1
    
    for i in range(1, len(data)):
        if data[i] == data[i-1]:
            count += 1
        else:
            encoded.append((data[i-1], count))
            count = 1
    
    encoded.append((data[-1], count))
    return encoded

# Exercise 6: DCT Class
class DCT:
    """Discrete Cosine Transform implementation"""
    
    def __init__(self, size=8):
        self.N = size
        self.T = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                if i == 0:
                    self.T[i,j] = 1 / np.sqrt(size)
                else:
                    self.T[i,j] = np.sqrt(2/size) * np.cos((2*j+1)*i*np.pi/(2*size))
    
    def encode(self, block):
        return self.T @ block @ self.T.T
    
    def decode(self, coeffs):
        return self.T.T @ coeffs @ self.T

# Exercise 7: DWT Class
class DWT:
    """Discrete Wavelet Transform implementation"""
    
    def encode(self, signal):
        n = len(signal)
        approx = []
        detail = []
        
        for i in range(n//2):
            a = (signal[2*i] + signal[2*i+1]) / np.sqrt(2)
            d = (signal[2*i] - signal[2*i+1]) / np.sqrt(2)
            approx.append(a)
            detail.append(d)
        
        return approx, detail
    
    def decode(self, approx, detail):
        signal = []
        for i in range(len(approx)):
            f1 = (approx[i] + detail[i]) / np.sqrt(2)
            f2 = (approx[i] - detail[i]) / np.sqrt(2)
            signal.extend([f1, f2])
        return signal

# Request models
class RGBRequest(BaseModel):
    r: float
    g: float
    b: float

class YUVRequest(BaseModel):
    y: float
    u: float
    v: float

class RLEData(BaseModel):
    data: Union[List, str]

# API Endpoints
@app.get("/")
def home():
    return {"message": "Image Processing API - Practice 1"}

# Exercise 2 endpoints
@app.post("/convert/rgb-to-yuv")
def rgb_to_yuv(request: RGBRequest):
    converter = ColorConverter()
    y, u, v = converter.rgb_to_yuv(request.r, request.g, request.b)
    return {"y": y, "u": u, "v": v}

@app.post("/convert/yuv-to-rgb")
def yuv_to_rgb(request: YUVRequest):
    converter = ColorConverter()
    r, g, b = converter.yuv_to_rgb(request.y, request.u, request.v)
    return {"r": r, "g": g, "b": b}

# Exercise 3 endpoint - Processes S1 action
@app.post("/image/resize")
def resize_image(width: int = 400, height: int = 300):
    """Resize image using Docker FFmpeg"""
    if not os.path.exists(INPUT_IMAGE):
        raise HTTPException(404, "Input image not found")
    
    success = resize_with_docker(width, height)
    
    if success:
        return {"status": "success", "output": OUTPUT_RESIZED}
    else:
        raise HTTPException(500, "Docker FFmpeg processing failed")

# Exercise 4 endpoint
@app.get("/image/serpentine")
def serpentine_read():
    """Read image bytes in serpentine order"""
    if not os.path.exists(INPUT_IMAGE):
        raise HTTPException(404, "Input image not found")
    
    bytes_data = read_serpentine(INPUT_IMAGE)
    return {"bytes": bytes_data[:20]}  # Return first 20 bytes for brevity

# Exercise 5.1 endpoint - Processes S1 action
@app.post("/image/convert-bw")
def convert_to_bw():
    """Convert image to black and white using Docker FFmpeg"""
    if not os.path.exists(INPUT_IMAGE):
        raise HTTPException(404, "Input image not found")
    
    success = convert_bw_docker()
    
    if success:
        return {"status": "success", "output": OUTPUT_BW}
    else:
        raise HTTPException(500, "Docker FFmpeg processing failed")

# Exercise 5.2 endpoint
@app.post("/encode/rle")
def rle_encode(request: RLEData):
    """Run-length encoding"""
    encoded = run_length_encode(request.data)
    return {"encoded": encoded}

# Exercise 6 endpoints
@app.post("/dct/encode")
def dct_encode(block: List[List[float]]):
    """DCT encoding"""
    dct = DCT()
    block_np = np.array(block)
    encoded = dct.encode(block_np)
    return {"coefficients": encoded.tolist()}

# Exercise 7 endpoints
@app.post("/dwt/encode")
def dwt_encode(signal: List[float]):
    """DWT encoding"""
    dwt = DWT()
    approx, detail = dwt.encode(signal)
    return {"approximation": approx, "detail": detail}

# Docker status check
@app.get("/docker/status")
def docker_status():
    """Check if Docker containers are running"""
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=practice1'], 
                              capture_output=True, text=True)
        return {"containers": result.stdout}
    except:
        return {"error": "Docker not available"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)