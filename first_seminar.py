import subprocess

class ColorConverter: 
    def from_rgb_to_yuv(self, r, g, b):
        """Convert RGB color to YUV color space."""
        y = 0.299 * r + 0.587 * g + 0.114 * b
        u = -0.14713 * r - 0.28886 * g + 0.436 * b
        v = 0.615 * r - 0.51499 * g - 0.10001 * b
        return (y, u, v)
    
    def from_yuv_to_rgb(self, y, u, v):
        """Convert YUV color to RGB color space."""
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

resize_image('input.jpg', 'output.jpg', 400, 300)  # Example usage