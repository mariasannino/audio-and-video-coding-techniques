import subprocess
import numpy as np
import unittest
from unittest.mock import patch
import tempfile
import os


# EXERCISE 2: RGB/YUV Converter Class
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


# EXERCISE 3: Image Resize with FFmpeg
# Reference: https://smarttech101.com/ffmpeg-compress-rescale-video-and-image
def resize_image(input_image, output_image, width, height):
    command = [
        'ffmpeg',
        '-y',
        '-i', input_image,
        '-vf', f'scale={width}:{height}',
        output_image,
    ]
    subprocess.run(command)

# EXERCISE 4: JPEG Serpentine Byte Reading
# Reference: https://yasoob.me/posts/understanding-and-writing-jpeg-decoder-in-python/
def serpentine(file_path):
    # Standard JPEG zigzag order
    zigzag = [0,1,5,6,14,15,27,28,
              2,4,7,13,16,26,29,42,
              3,8,12,17,25,30,41,43,
              9,11,18,24,31,40,44,53,
              10,19,23,32,39,45,52,54,
              20,22,33,38,46,51,55,60,
              21,34,37,47,50,56,59,61,
              35,36,48,49,57,58,62,63]
    with open(file_path, 'rb') as f:
        data = f.read()
        # Take first 64 bytes and read in zigzag order
        result = [data[zigzag[i]] for i in range(64)]
        print(result)
        return result


# EXERCISE 5.1: Black & White Conversion with Heavy Compression
# Reference: https://smarttech101.com/ffmpeg-compress-rescale-video-and-image
def convert_bw_heavy_compression(input_image, output_image):
    command = [
        'ffmpeg',
        '-y',
        '-i', input_image,
        '-vf', 'format=gray',  # Convert to B/W
        '-qscale:v', '31',     # Maximum compression (worst quality)
        output_image,
    ]
    subprocess.run(command)


# EXERCISE 5.2: Run-Length Encoding
def run_length_encode(data):
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


# EXERCISE 6: Discrete Cosine Transform (DCT) Class
# Reference: https://www.math.cuhk.edu.hk/~lmlui/dct.pdf
class DCT:
    def __init__(self, N=8):
        self.N = N
        # Create DCT matrix T from Eq. 4
        self.T = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i == 0:
                    self.T[i, j] = 1 / np.sqrt(N)  # Eq. 4 case 1
                else:
                    # Eq. 4 case 2
                    self.T[i, j] = np.sqrt(2/N) * np.cos((2*j + 1) * i * np.pi / (2*N))
    
    def encode(self, block):
        D = self.T @ block @ self.T.T
        return D
    
    def decode(self, dct_coeffs):
        D = self.T.T @ dct_coeffs @ self.T
        return D


# EXERCISE 7: Discrete Wavelet Transform (DWT) Class
# Reference: https://dsp-book.narod.ru/PWSA/8276_01.pdf
class DWT:
    def encode(self, signal):
        # Forward Haar Transform using Formula (1.2) and (1.3)
        N = len(signal)
        approx = []  # First trend a1
        detail = []  # First fluctuation d1
        
        for m in range(1, N//2 + 1):
            # Formula (1.2)
            a_m = (signal[2*m-2] + signal[2*m-1]) / (2**0.5)
            # Formula (1.3)  
            d_m = (signal[2*m-2] - signal[2*m-1]) / (2**0.5)
            approx.append(a_m)
            detail.append(d_m)
        
        return approx, detail
    
    def decode(self, approx, detail):
        # Inverse Haar Transform using Formula (1.6)
        signal = []
        
        for m in range(len(approx)):
            f1 = (approx[m] + detail[m]) / (2**0.5)
            f2 = (approx[m] - detail[m]) / (2**0.5)
            signal.extend([f1, f2])
        
        return signal


# EXERCISE 8: UNIT TESTS FOR ALL METHODS AND CLASSES
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


# TESTING ALL EXERCISES

if __name__ == "__main__":
    print("=== Testing Exercise 2: RGB/YUV Converter ===")
    converter = ColorConverter()
    print("RGB to YUV:", converter.from_rgb_to_yuv(255, 0, 0))  # Example 
    print("YUV to RGB:", converter.from_yuv_to_rgb(162, 94, 224))  # Example 
    
    print("\n=== Testing Exercise 3: Image Resize ===")
    resize_image('input.jpg', 'output_resize_image.jpg', 400, 300)  
    
    print("\n=== Testing Exercise 4: Serpentine Reading ===")
    serpentine("input.jpg") 
    
    print("\n=== Testing Exercise 5.1: B/W Conversion ===")
    convert_bw_heavy_compression('input.jpg', 'output_bw_compress.jpg') 
    
    print("\n=== Testing Exercise 5.2: Run-Length Encoding ===")
    test1 = [1,1,1,2,2,3,4,4,4,4,5]
    test2 = "AAAABBBCCDAA"
    test3 = "11112222333111"
    print("Test 1:", run_length_encode(test1))
    print("Test 2:", run_length_encode(test2))
    print("Test 3:", run_length_encode(test3))
    
    print("\n=== Testing Exercise 6: DCT ===")
    dct = DCT()
    test_block = np.ones((8, 8)) * 100
    encoded = dct.encode(test_block)
    print("Encoded DCT coefficients:\n", encoded)
    decoded = dct.decode(encoded)
    print("Decoded block:\n", decoded)
    print("Test block:\n", test_block)
    
    print("\n=== Testing Exercise 7: DWT ===")
    dwt = DWT()
    signal = [4, 6, 10, 12, 8, 6, 5, 5]
    print("Original signal f:", signal)
    approx, detail = dwt.encode(signal)
    print("Approximation a¹:", [round(x, 3) for x in approx])
    print("Detail d¹:", [round(x, 3) for x in detail])
    reconstructed = dwt.decode(approx, detail)
    print("Reconstructed f:", [round(x, 3) for x in reconstructed])
    
    print("\n=== Running Unit Tests ===")
    # Run the unit tests
    unittest.main(argv=[''], verbosity=2, exit=False)