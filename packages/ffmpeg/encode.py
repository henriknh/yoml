FFMPEG_BIN = "bin/ffmpeg.exe" # on Windows
MKV = 'video.mkv'
MP4 = 'video.mp4'
OUTPUT = 'output.mkv'

import subprocess as sp

VP9_DASH_PARAMS="-tile-columns 4 -frame-parallel 1"
'''
#command = [FFMPEG_BIN,
           '-i', 'video.mkv', # The imput comes from a pipe
           '-movflags', '+faststart',
           #'-s', '420x360', # size of one frame
           '-r', '24', # frames per second
           '-g', '48',
           '-vcodec', 'libvpx-vp9',
           '-acodec', 'libvorbis',
           '-s', '160x90',
           '-b:v', '250k',
           '-keyint_min', '150',
           '-g', '150',
           '-tile-columns', '4',
           '-frame-parallel', '1',
           '-an', '',

           '-maxrate', '2000k',
           '-bufsize', '4000k',
           '-b:a', '128k',
           '-crf', '23',	#18 is often considered to be roughly "visually lossless", 23 is the default
           '-preset', 'veryfast',	#ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow          
           OUTPUT]
'''


command = "bin/ffmpeg -i video.mkv -c:v libvpx-vp9 -s 1280x720 -b:v 1500k -keyint_min 150 -g 150 " + VP9_DASH_PARAMS + " -an -f webm -dash 1 video_1280x720_500k.webm"
proc = sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE)