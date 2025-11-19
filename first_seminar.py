import subprocess

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

converter = ColorConverter()
print("rgb to YUV:", converter.from_rgb_to_yuv(255, 0, 0))  # Example 
print("YUV to rgb:", converter.from_yuv_to_rgb(162, 94, 224))  # Example 

# Method defined following: https://smarttech101.com/ffmpeg-compress-rescale-video-and-image
def resize_image(input_image, output_image, width, height):
    command = [
        'ffmpeg',
        '-y',
        '-i', input_image,
        '-vf', f'scale={width}:{height}',
        output_image,
    ]
    subprocess.run(command)

resize_image('input.jpg', 'output_resize_image.jpg', 400, 300)  # Example usage
#method defined following: https://yasoob.me/posts/understanding-and-writing-jpeg-decoder-in-python/

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
        print (result)
        return result

serpentine("input.jpg")
#Method defined following: https://smarttech101.com/ffmpeg-compress-rescale-video-and-image
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
convert_bw_heavy_compression('input.jpg', 'output_bw_compress.jpg')

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

# Test with different data
test1 = [1,1,1,2,2,3,4,4,4,4,5]
test2 = "AAAABBBCCDAA"
test3 = "11112222333111"
print("Test 1:", run_length_encode(test1))
print("Test 2:", run_length_encode(test2))
print("Test 3:", run_length_encode(test3))