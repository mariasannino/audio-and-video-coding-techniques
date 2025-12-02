from flask import Flask
import os
import subprocess
import json
import tempfile

app = Flask(__name__)

BBB_FULL = "big_buck_bunny.mp4"

@app.route('/')
def home():
    return '''
    <h1>Big Buck Bunny - 7 Tasks</h1>
    <ol>
        <li><a href="/task1/640/480">Task 1: Resolution (640x480)</a></li>
        <li><a href="/task2/420">Task 2: Chroma 4:2:0</a></li>
        <li><a href="/task3">Task 3: Video Info</a></li>
        <li><a href="/task4">Task 4: Create Container (20s)</a></li>
        <li><a href="/task5">Task 5: Count Tracks</a></li>
        <li><a href="/task6">Task 6: Macroblocks</a></li>
        <li><a href="/task7">Task 7: YUV Histogram</a></li>
    </ol>
    '''

@app.route('/task1/<width>/<height>')
def task1(width, height):
    output = f"temp_res_{width}x{height}.mp4"
    os.system(f"ffmpeg -i {BBB_FULL} -vf scale={width}:{height} -c:a copy {output}")
    return f"Created: {output}<br><a href='/'>Back</a>"

@app.route('/task2/<subsampling>')
def task2(subsampling):
    formats = {"420": "yuv420p", "422": "yuv422p", "444": "yuv444p"}
    output = f"temp_chroma_{subsampling}.mp4"
    os.system(f"ffmpeg -i {BBB_FULL} -pix_fmt {formats[subsampling]} -c:a copy {output}")
    return f"Created: {output}<br><a href='/'>Back</a>"

@app.route('/task3')
def task3():
    cmd = f"ffprobe -v quiet -print_format json -show_streams -show_format {BBB_FULL}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        return "Error"
    
    data = json.loads(result.stdout)
    
    info = []
    if 'format' in data:
        fmt = data['format']
        info.append(f"1. Duration: {float(fmt.get('duration', 0)):.2f}s")
        info.append(f"2. Size: {int(fmt.get('size', 0))/(1024*1024):.1f}MB")
        info.append(f"3. Bitrate: {int(fmt.get('bit_rate', 0))/1000:.0f}kbps")
    
    if 'streams' in data:
        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                info.append(f"4. Resolution: {stream.get('width')}x{stream.get('height')}")
                info.append(f"5. Codec: {stream.get('codec_name')}")
    
    return "<br>".join(info) + "<br><a href='/'>Back</a>"

@app.route('/task4')
def task4():
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_video = os.path.join(tmpdir, "temp_20s.mp4")
        temp_aac = os.path.join(tmpdir, "aac.m4a")
        temp_mp3 = os.path.join(tmpdir, "mp3.mp3")
        temp_ac3 = os.path.join(tmpdir, "ac3.ac3")
        
        os.system(f"ffmpeg -i {BBB_FULL} -t 20 -c copy {temp_video}")
        os.system(f"ffmpeg -i {temp_video} -ac 1 -c:a aac {temp_aac}")
        os.system(f"ffmpeg -i {temp_video} -c:a mp3 -b:a 96k {temp_mp3}")
        os.system(f"ffmpeg -i {temp_video} -c:a ac3 {temp_ac3}")
        
        output = "task4_container_20s.mp4"
        cmd = f"ffmpeg -i {temp_video} -i {temp_aac} -i {temp_mp3} -i {temp_ac3} "
        cmd += f"-map 0:v -map 0:a -map 1 -map 2 -map 3 -c copy {output}"
        os.system(cmd)
    
    return f"Created: {output} (20s video + 3 audio tracks)<br><a href='/'>Back</a>"

@app.route('/task5')
def task5():
    cmd = f"ffprobe -v quiet -show_streams {BBB_FULL}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    video = result.stdout.count('codec_type=video')
    audio = result.stdout.count('codec_type=audio')
    
    return f"Video: {video}<br>Audio: {audio}<br>Total: {video+audio}<br><a href='/'>Back</a>"

@app.route('/task6')
def task6():
    output = f"temp_macroblocks.mp4"
  
    os.system(f"ffmpeg -i {BBB_FULL} -vf codecview=mv=pf+bf+bb:qp=1 -c:a copy {output}")
    
    return f"Created: {output}<br>Motion vectors (red/green) + Macroblocks (colored blocks)<br><a href='/'>Back</a>"

@app.route('/task7')
def task7():
    output = f"temp_histogram.mp4"
    os.system(f"ffmpeg -i {BBB_FULL} -vf histogram -c:a copy {output}")
    return f"Created: {output}<br><a href='/'>Back</a>"

if __name__ == '__main__':
    print("S2 MPEG4 - 7 Tasks")
    print("NO videos on GitHub - all outputs are temporary")
    app.run(debug=True, port=5000)