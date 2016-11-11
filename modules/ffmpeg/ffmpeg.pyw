import subprocess as subprocess
import uuid
import signal
import logging
import glob, os
import json
import time
import threading
from modules.util.util import *

PATH_FFMPEG = os.path.dirname(os.path.realpath(__file__)) + '\..\..\packages\\ffmpeg\\bin\\ffmpeg'
PATH_FFMPEG = 'packages\\ffmpeg\\bin\\ffmpeg'
PATH_FFPROBE = 'packages\\ffmpeg\\bin\\ffprobe'
PATH_MP4BOX = 'packages\\ffmpeg\\bin\\MP4Box'
PATH_SUBMARINE = 'packages\\submarine\\submarine'

class ffmpeg():

	procs = {}

	def __init__(self, config, subtitle):
		self.config = config
		self.subtitle = subtitle

		logging.info("FFMPEG started")

		self.clean_ffmpeg()

	def run_ffmpeg(self, input, time=0):

		output = str(uuid.uuid4())

		# Download subtitle
		if self.config.get_config_by_config('display_subtitle')['value'] == '1' and self.subtitle != None:
			subtitle_language = [x.strip() for x in self.config.get_config_by_config('display_subtitle_language')['value'].split(',')]
			self.subtitle.handle_sub(input, output, subtitle_language, -1*int(time))

		#Funkar bra
		#command = PATH_FFMPEG + ' -loglevel info -y -ss ' + str(time) + ' -i "' + input + '" -codec copy -bsf h264_mp4toannexb -c:a aac -b:a 128k -map 0 -f segment -segment_format mpegts -segment_list www/static/temp/"' + output + '".m3u8 -segment_time 2 -segment_list_type m3u8 www/static/temp/"' + output + '"-%d.ts'
		command = PATH_FFMPEG + ' -loglevel info -y -ss ' + str(time) + ' -i "' + input + '" -codec copy -bsf h264_mp4toannexb -c:a aac -b:a 128k -map 0 -f segment -segment_format mpegts -segment_list www/static/temp/"' + output + '".m3u8 -segment_time 2 -segment_time_delta 0.05 -segment_list_type m3u8 www/static/temp/"' + output + '"-%d.ts'

		proc = subprocess.Popen(command, shell=False)

		self.procs[output] = [proc.pid, input]

		logging.info("FFMPEG script running, output name is " + str(output))
		logging.info(self.procs)

		return str(output)

	def clean_ffmpeg(self, input=''):
		logging.info("FFMPEG clean ffmpeg temp for input: " + input + " (might be '')")
		filelist = glob.glob("www/static/temp/" + input + "*")
		for f in filelist:
			if os.path.isfile(f):
				os.remove(f)


	def stop_all_transcoding(self):
		logging.info("FFMPEG stop all transcoding")

		for m3u8, value in self.procs.iteritems():
			os.kill(int(value[0]), signal.SIGTERM)
		time.sleep(1)

		self.procs.clear()
		time.sleep(1)

		self.clean_ffmpeg()

	def stop_transcoding(self, m3u8):
		logging.info("FFMPEG stop transcoding for %s" % m3u8)

		proc = self.procs.pop(m3u8)

		try:
			os.kill(int(proc[0]), signal.SIGTERM)
			time.sleep(1)
		except:
			logging.info('Process already terminated')

		self.clean_ffmpeg(m3u8)

		return proc[1]

	def probe(self, vid_file_path):
	    ''' Give a json from ffprobe command line

	    @vid_file_path : The absolute (full) path of the video file, string.
	    '''
	    if type(vid_file_path) != str:
	        raise Exception('Give ffprobe a full file path of the video')
	        return

	    command = [PATH_FFPROBE,
	            "-loglevel",  "quiet",
	            "-print_format", "json",
	             "-show_format",
	             "-show_streams",
	             vid_file_path
	             ]

	    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	    out, err = pipe.communicate()
	    return json.loads(out)


	def duration(self, vid_file_path):
	    ''' Video's duration in seconds, return a float number
	    '''
	    _json = self.probe(str(vid_file_path))

	    if 'format' in _json:
	        if 'duration' in _json['format']:
	            return float(_json['format']['duration'])

	    if 'streams' in _json:
	        # commonly stream 0 is the video
	        for s in _json['streams']:
	            if 'duration' in s:
	                return float(s['duration'])
