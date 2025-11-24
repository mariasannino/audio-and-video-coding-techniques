 # main.py - COMPLETE API WITH ALL PREVIOUS WORK AND UNIT TESTS
from typing import Union, List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import numpy as np
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import json
import uvicorn
import shutil
from pathlib import Path

app = FastAPI(
    title="Image Processing API",
    description="Complete API integrating all previous image processing work including RGB/YUV conversion, DCT, DWT, and encoding methods",
    version="1.0.0"
)

# ============ PREDEFINED PATHS ============
PREDEFINED_PATHS = {
    "input_image": "input_files/input.jpg",
    "output_resized": "output_files/resized_output.jpg", 
    "output_bw": "output_files/bw_output.jpg",
    "test_binary": "input_files/test_data.bin"
}

# ============ EXERCISE 2: RGB/YUV Converter Class ============
class ColorConverter:
    def from_rgb_to_yuv(self, r, g, b):
        y = 0.299 * r + 0.587 * g + 0.114 * b
        u = -0.14713 * r - 0.28886 * g + 0.436 * b
        v = 0.615 * r - 0.51499 * g - 0.10001 * b
        return (y, u, v)
    
    def from_yuv_to_rgb(self, y, u, v):
        r = y + 1.140 * (v - 128)
        g = y - 0.395 * (u - 128) - 0.581 * (v - 128)
        b = y + 2.032 * (u - 128)
        return (r, g, b)

# ============ EXERCISE 3: Image Resize with FFmpeg ============
def resize_image(input_image: str, output_image: str, width: int, height: int) -> Dict[str, Any]:
    """Resize image using FFmpeg"""
    try:
        command = [
            'ffmpeg',
            '-y',
            '-i', input_image,
            '-vf', f'scale={width}:{height}',
            output_image,
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============ EXERCISE 4: JPEG Serpentine Byte Reading ============
def serpentine(file_path: str) -> List[int]:
    """Read JPEG file in serpentine (zigzag) order"""
    zigzag = [
        0, 1, 5, 6, 14, 15, 27, 28,
        2, 4, 7, 13, 16, 26, 29, 42,
        3, 8, 12, 17, 25, 30, 41, 43,
        9, 11, 18, 24, 31, 40, 44, 53,
        10, 19, 23, 32, 39, 45, 52, 54,
        20, 22, 33, 38, 46, 51, 55, 60,
        21, 34, 37, 47, 50, 56, 59, 61,
        35, 36, 48, 49, 57, 58, 62, 63
    ]
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            result = [data[zigzag[i]] if zigzag[i] < len(data) else 0 for i in range(64)]
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

# ============ EXERCISE 5.1: Black & White Conversion ============
def convert_bw_heavy_compression(input_image: str, output_image: str) -> Dict[str, Any]:
    """Convert image to black and white with heavy compression"""
    try:
        command = [
            'ffmpeg',
            '-y',
            '-i', input_image,
            '-vf', 'format=gray',
            '-qscale:v', '31',
            output_image,
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============ EXERCISE 5.2: Run-Length Encoding ============
def run_length_encode(data: Union[List[Any], str]) -> List[tuple]:
    """Perform run-length encoding on data"""
    if isinstance(data, str):
        data = list(data)
    
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

# ============ EXERCISE 6: Discrete Cosine Transform (DCT) Class ============
class DCT:
    def __init__(self, N: int = 8):
        self.N = N
        self.T = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i == 0:
                    self.T[i, j] = 1 / np.sqrt(N)
                else:
                    self.T[i, j] = np.sqrt(2/N) * np.cos((2*j + 1) * i * np.pi / (2*N))
    
    def encode(self, block: np.ndarray) -> np.ndarray:
        D = self.T @ block @ self.T.T
        return D
    
    def decode(self, dct_coeffs: np.ndarray) -> np.ndarray:
        D = self.T.T @ dct_coeffs @ self.T
        return D

# ============ EXERCISE 7: Discrete Wavelet Transform (DWT) Class ============
class DWT:
    def encode(self, signal: List[float]) -> tuple:
        N = len(signal)
        if N % 2 != 0:
            raise ValueError("Signal length must be even for DWT")
            
        approx = []
        detail = []
        
        for m in range(N // 2):
            a_m = (signal[2*m] + signal[2*m + 1]) / np.sqrt(2)
            d_m = (signal[2*m] - signal[2*m + 1]) / np.sqrt(2)
            approx.append(a_m)
            detail.append(d_m)
        
        return approx, detail
    
    def decode(self, approx: List[float], detail: List[float]) -> List[float]:
        if len(approx) != len(detail):
            raise ValueError("Approximation and detail must have same length")
            
        signal = []
        
        for m in range(len(approx)):
            f1 = (approx[m] + detail[m]) / np.sqrt(2)
            f2 = (approx[m] - detail[m]) / np.sqrt(2)
            signal.extend([f1, f2])
        
        return signal

# ============ Pydantic Models for API ============
class RGBRequest(BaseModel):
    r: float
    g: float
    b: float

class YUVRequest(BaseModel):
    y: float
    u: float
    v: float

class RLERequest(BaseModel):
    data: Union[List[Any], str]

class DCTRequest(BaseModel):
    block: List[List[float]]

class DWTEncodeRequest(BaseModel):
    signal: List[float]

class DWTDecodeRequest(BaseModel):
    approximation: List[float]
    detail: List[float]

# ============ API ENDPOINTS ============
@app.get("/")
def read_root():
    return {
        "message": "Image Processing API - All Exercises Integrated",
        "predefined_paths": PREDEFINED_PATHS,
        "endpoints": {
            "color_conversion": ["POST /color/rgb-to-yuv", "POST /color/yuv-to-rgb"],
            "image_processing": [
                "POST /image/resize", 
                "GET /image/serpentine", 
                "POST /image/convert-bw"
            ],
            "encoding": ["POST /encoding/run-length"],
            "transforms": [
                "POST /dct/encode", 
                "POST /dct/decode", 
                "POST /dwt/encode", 
                "POST /dwt/decode"
            ],
            "testing": ["GET /test/all", "GET /run-unit-tests", "GET /test-exercise/{exercise_id}"],
            "setup": ["GET /status", "POST /setup/create-test-file"]
        }
    }

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# Exercise 2 Endpoints
@app.post("/color/rgb-to-yuv")
def api_rgb_to_yuv(request: RGBRequest):
    converter = ColorConverter()
    y, u, v = converter.from_rgb_to_yuv(request.r, request.g, request.b)
    return {
        "input_rgb": {"r": request.r, "g": request.g, "b": request.b},
        "output_yuv": {"y": round(y, 4), "u": round(u, 4), "v": round(v, 4)}
    }

@app.post("/color/yuv-to-rgb")
def api_yuv_to_rgb(request: YUVRequest):
    converter = ColorConverter()
    r, g, b = converter.from_yuv_to_rgb(request.y, request.u, request.v)
    return {
        "input_yuv": {"y": request.y, "u": request.u, "v": request.v},
        "output_rgb": {"r": round(r, 4), "g": round(g, 4), "b": round(b, 4)}
    }

# Exercise 3 Endpoint - Simplified with predefined paths
@app.post("/image/resize")
def api_resize_image(width: int = 400, height: int = 300):
    """Resize the predefined input image"""
    input_path = PREDEFINED_PATHS["input_image"]
    output_path = PREDEFINED_PATHS["output_resized"]
    
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail=f"Input file not found: {input_path}. Please place your image in this location.")
    
    result = resize_image(input_path, output_path, width, height)
    
    if result["success"]:
        return {
            "status": "success",
            "input": input_path,
            "output": output_path,
            "dimensions": f"{width}x{height}",
            "message": "Image resized successfully"
        }
    else:
        raise HTTPException(status_code=500, detail=f"FFmpeg error: {result.get('error', result.get('stderr', 'Unknown error'))}")

# Exercise 4 Endpoint - Simplified with predefined paths
@app.get("/image/serpentine")
def api_serpentine():
    """Read predefined test file in serpentine order"""
    file_path = PREDEFINED_PATHS["test_binary"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Test file not found: {file_path}. Use /setup/create-test-file to create it.")
    
    result = serpentine(file_path)
    return {
        "file_path": file_path,
        "serpentine_bytes": result,
        "message": "First 64 bytes read in zigzag order"
    }

# Exercise 5.1 Endpoint - Simplified with predefined paths
@app.post("/image/convert-bw")
def api_convert_bw():
    """Convert predefined input image to black and white"""
    input_path = PREDEFINED_PATHS["input_image"]
    output_path = PREDEFINED_PATHS["output_bw"]
    
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail=f"Input file not found: {input_path}. Please place your image in this location.")
    
    result = convert_bw_heavy_compression(input_path, output_path)
    
    if result["success"]:
        return {
            "status": "success", 
            "input": input_path,
            "output": output_path,
            "message": "Image converted to black and white with heavy compression"
        }
    else:
        raise HTTPException(status_code=500, detail=f"FFmpeg error: {result.get('error', result.get('stderr', 'Unknown error'))}")

# Exercise 5.2 Endpoint
@app.post("/encoding/run-length")
def api_run_length_encode(request: RLERequest):
    result = run_length_encode(request.data)
    return {
        "original_data": request.data,
        "encoded": result,
        "compression_ratio": f"{len(request.data)} -> {len(result)} elements"
    }

# Exercise 6 Endpoints
@app.post("/dct/encode")
def api_dct_encode(request: DCTRequest):
    try:
        dct = DCT()
        block = np.array(request.block)
        if block.shape != (8, 8):
            raise HTTPException(status_code=400, detail="Block must be 8x8")
        encoded = dct.encode(block)
        return {
            "original_block": request.block,
            "dct_coefficients": encoded.tolist(),
            "message": "DCT encoding completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dct/decode")
def api_dct_decode(request: DCTRequest):
    try:
        dct = DCT()
        dct_coeffs = np.array(request.block)
        if dct_coeffs.shape != (8, 8):
            raise HTTPException(status_code=400, detail="DCT coefficients must be 8x8")
        decoded = dct.decode(dct_coeffs)
        return {
            "dct_coefficients": request.block,
            "decoded_block": decoded.tolist(),
            "message": "DCT decoding completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Exercise 7 Endpoints
@app.post("/dwt/encode")
def api_dwt_encode(request: DWTEncodeRequest):
    try:
        dwt = DWT()
        signal = request.signal
        if len(signal) % 2 != 0:
            raise HTTPException(status_code=400, detail="Signal length must be even")
        approx, detail = dwt.encode(signal)
        return {
            "original_signal": signal,
            "approximation": [float(x) for x in approx],
            "detail": [float(x) for x in detail],
            "message": "DWT encoding completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dwt/decode")
def api_dwt_decode(request: DWTDecodeRequest):
    try:
        dwt = DWT()
        approx = request.approximation
        detail = request.detail
        
        if len(approx) != len(detail):
            raise HTTPException(status_code=400, detail="Approximation and detail must have same length")
            
        reconstructed = dwt.decode(approx, detail)
        return {
            "approximation": approx,
            "detail": detail,
            "reconstructed_signal": [float(x) for x in reconstructed],
            "message": "DWT decoding completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ SETUP ENDPOINTS ============
@app.get("/status")
def get_status():
    """Check status of predefined files"""
    status = {}
    for name, path in PREDEFINED_PATHS.items():
        exists = os.path.exists(path)
        status[name] = {
            "path": path,
            "exists": exists,
            "size": os.path.getsize(path) if exists else 0
        }
    
    # Check FFmpeg availability
    ffmpeg_available = shutil.which("ffmpeg") is not None
    status["ffmpeg_available"] = ffmpeg_available
    
    return status

@app.post("/setup/create-test-file")
def create_test_file():
    """Create the test binary file for serpentine testing"""
    file_path = PREDEFINED_PATHS["test_binary"]
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create test binary data
    with open(file_path, "wb") as f:
        f.write(bytes(range(100)))  # 0 to 99 bytes
    
    return {
        "status": "success",
        "file_created": file_path,
        "file_size": 100,
        "message": "Test binary file created for serpentine testing"
    }

# ============ TESTING ENDPOINTS ============
@app.get("/test/all")
def test_all_functionality():
    """Test all functionality and return results"""
    results = {}
    
    # Test Exercise 2: Color Converter
    converter = ColorConverter()
    results["exercise_2_color_converter"] = {
        "rgb_to_yuv": converter.from_rgb_to_yuv(255, 0, 0),
        "yuv_to_rgb": converter.from_yuv_to_rgb(162, 94, 224)
    }
    
    # Test Exercise 5.2: Run-Length Encoding
    test_data = [1,1,1,2,2,3,4,4,4,4,5]
    results["exercise_5_2_run_length_encoding"] = {
        "input": test_data,
        "output": run_length_encode(test_data)
    }
    
    # Test Exercise 6: DCT
    dct = DCT()
    test_block = np.ones((8, 8)) * 100
    encoded_dct = dct.encode(test_block)
    decoded_dct = dct.decode(encoded_dct)
    results["exercise_6_dct"] = {
        "original_block_mean": float(np.mean(test_block)),
        "encoded_dct_mean": float(np.mean(encoded_dct)),
        "reconstruction_success": bool(np.allclose(decoded_dct, test_block, atol=1e-5))
    }
    
    # Test Exercise 7: DWT
    dwt = DWT()
    signal = [4, 6, 10, 12, 8, 6, 5, 5]
    approx, detail = dwt.encode(signal)
    reconstructed = dwt.decode(approx, detail)
    results["exercise_7_dwt"] = {
        "original_signal": signal,
        "approximation": [float(x) for x in approx],
        "detail": [float(x) for x in detail],
        "reconstructed_signal": [float(x) for x in reconstructed],
        "reconstruction_success": bool(np.allclose(reconstructed, signal, atol=1e-5))
    }
    
    return {
        "status": "all_tests_completed",
        "results": results
    }

@app.get("/test-exercise/{exercise_id}")
def test_specific_exercise(exercise_id: int):
    """Test specific exercise by ID"""
    if exercise_id == 2:
        converter = ColorConverter()
        return {"exercise_2": {
            "rgb_to_yuv": converter.from_rgb_to_yuv(255, 0, 0),
            "yuv_to_rgb": converter.from_yuv_to_rgb(162, 94, 224)
        }}
    elif exercise_id == 5:
        test_data = [1,1,1,2,2,3,4,4,4,4,5]
        return {"exercise_5": {
            "run_length_encoding": run_length_encode(test_data)
        }}
    elif exercise_id == 6:
        dct = DCT()
        test_block = np.ones((8, 8)) * 100
        encoded = dct.encode(test_block)
        decoded = dct.decode(encoded)
        return {"exercise_6": {
            "reconstruction_success": bool(np.allclose(decoded, test_block, atol=1e-5))
        }}
    elif exercise_id == 7:
        dwt = DWT()
        signal = [4, 6, 10, 12, 8, 6, 5, 5]
        approx, detail = dwt.encode(signal)
        reconstructed = dwt.decode(approx, detail)
        return {"exercise_7": {
            "reconstruction_success": bool(np.allclose(reconstructed, signal, atol=1e-5))
        }}
    else:
        raise HTTPException(status_code=404, detail="Exercise not found")

# ============ UNIT TESTS AS API ENDPOINT ============
class TestExercise2ColorConverter(unittest.TestCase):
    def test_from_rgb_to_yuv(self):
        converter = ColorConverter()
        y, u, v = converter.from_rgb_to_yuv(255, 0, 0)
        self.assertAlmostEqual(y, 76.245, places=2)
    
    def test_from_yuv_to_rgb(self):
        converter = ColorConverter()
        r, g, b = converter.from_yuv_to_rgb(162, 94, 224)
        self.assertEqual(len([r, g, b]), 3)

class TestExercise3ResizeImage(unittest.TestCase):
    @patch('subprocess.run')
    def test_resize_image(self, mock_subprocess):
        resize_image('input.jpg', 'output.jpg', 400, 300)
        mock_subprocess.assert_called_once()

class TestExercise4Serpentine(unittest.TestCase):
    def test_serpentine(self):
        test_data = bytes(range(64))
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
            f.write(test_data)
            temp_file = f.name
        try:
            result = serpentine(temp_file)
            self.assertEqual(len(result), 64)
        finally:
            os.unlink(temp_file)

class TestExercise5_1ConvertBW(unittest.TestCase):
    @patch('subprocess.run')
    def test_convert_bw_heavy_compression(self, mock_subprocess):
        convert_bw_heavy_compression('input.jpg', 'output.jpg')
        mock_subprocess.assert_called_once()

class TestExercise5_2RunLengthEncode(unittest.TestCase):
    def test_run_length_encode_numeric(self):
        test1 = [1,1,1,2,2,3,4,4,4,4,5]
        result = run_length_encode(test1)
        expected = [(1,3), (2,2), (3,1), (4,4), (5,1)]
        self.assertEqual(result, expected)
    
    def test_run_length_encode_string(self):
        test2 = "AAAABBBCCDAA"
        result = run_length_encode(test2)
        expected = [('A',4), ('B',3), ('C',2), ('D',1), ('A',2)]
        self.assertEqual(result, expected)

class TestExercise6DCT(unittest.TestCase):
    def test_dct_encode_decode(self):
        dct = DCT()
        test_block = np.ones((8, 8)) * 100
        encoded = dct.encode(test_block)
        decoded = dct.decode(encoded)
        np.testing.assert_array_almost_equal(decoded, test_block, decimal=5)

class TestExercise7DWT(unittest.TestCase):
    def test_dwt_encode_decode(self):
        dwt = DWT()
        signal = [4, 6, 10, 12, 8, 6, 5, 5]
        approx, detail = dwt.encode(signal)
        reconstructed = dwt.decode(approx, detail)
        np.testing.assert_array_almost_equal(reconstructed, signal, decimal=5)

@app.get("/run-unit-tests")
def run_unit_tests():
    """Run all unit tests and return results"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestExercise2ColorConverter))
    test_suite.addTest(unittest.makeSuite(TestExercise3ResizeImage))
    test_suite.addTest(unittest.makeSuite(TestExercise4Serpentine))
    test_suite.addTest(unittest.makeSuite(TestExercise5_1ConvertBW))
    test_suite.addTest(unittest.makeSuite(TestExercise5_2RunLengthEncode))
    test_suite.addTest(unittest.makeSuite(TestExercise6DCT))
    test_suite.addTest(unittest.makeSuite(TestExercise7DWT))
    
    runner = unittest.TextTestRunner(verbosity=2, stream=None)
    result = runner.run(test_suite)
    
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "successful": result.wasSuccessful(),
        "failure_details": [str(f[1]) for f in result.failures] if result.failures else [],
        "error_details": [str(e[1]) for e in result.errors] if result.errors else []
    }

# ============ MAIN EXECUTION ============
def setup_environment():
    """Create necessary directories"""
    Path("input_files").mkdir(exist_ok=True)
    Path("output_files").mkdir(exist_ok=True)
    print("✅ Directories created: input_files/, output_files/")

if __name__ == "__main__":
    setup_environment()
    print("Starting Image Processing API with all integrated exercises...")
    print("Predefined paths:")
    for name, path in PREDEFINED_PATHS.items():
        print(f"  {name}: {path}")
    print("Visit http://localhost:8000/docs for API documentation")
    print("Use /status endpoint to check file availability")
    uvicorn.run(app, host="0.0.0.0", port=8000)