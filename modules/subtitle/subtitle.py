from packages.opensubtitles.opensubtitles import OpenSubtitles
from packages.submarine.parser import *
from packages.pysrt.srtfile import *
from modules.util.util import *

from packages.opensubtitles.utils import File
import logging, os, zipfile, fileinput

PATH_SRT_SHIFT = 'packages\\srt_shift\\srt_shift.py'

class Subtitle():

	def __init__(self, username, password):

		self.subtitle = OpenSubtitles()
		self.login(username, password)

	def login(self, username, password):
		logging.info('Login to OpenSubtitle')
		self.token = self.subtitle.login(username, password)
		logging.info("OpenSubtitle token: " + self.token)

	def handle_sub(self, file_path, output, subtitle_language, shift=0):
		logging.info('Handling subtitle for languages ' + str(subtitle_language) + ' and for file ' + file_path)
		for language in subtitle_language:
			srt_file = self.download_subtitle(file_path, output, language)
			if srt_file == -1:
				return
			self.shift(srt_file, int(shift))
			self.convert_vtt(srt_file)

	def download_subtitle(self, path, output, language):

		logging.info("download subtitle: " + path)

		f = File(path)
		hash = f.get_hash()
		size = f.size
		data = self.subtitle.search_subtitles([{'moviehash': hash, 'moviebytesize': size}])

		if data == None:
			return -1
		
		dllink = None
		for sub in data:
			if sub['ISO639'] == language:
				dllink = sub['ZipDownloadLink']

		if dllink == None:
			return -1
	
		zip = os.getcwd() + '/www/static/temp/' + output + '.zip'
		srt_dest = os.getcwd() + '/www/static/temp/' + output + '.' + language + '.srt'

		download(dllink, zip)

		zf = zipfile.ZipFile(zip, 'r')

		for file in zf.namelist():
			if file.lower().endswith('.srt'):
				srt = open(srt_dest, "w")
				data = zf.read(file).splitlines()

				for line in data:
					srt.write(line+'\n')
				srt.close()

		return srt_dest

	def shift(self, srt_file, shift):

		def parse_time(time):
			hour, minute, second = time.split(':')
			hour, minute = int(hour), int(minute)
			second_parts = second.split(',')
			second = int(second_parts[0])
			microsecond = int(second_parts[1])
			return [hour, minute, second, microsecond]
		def shift_time(time):
			time[1] += (time[2] + shift) / 60
			time[2] = (time[2] + shift) % 60
			return time

		for line in fileinput.input(srt_file, inplace = 1):
			if ' --> ' in line:
				start, end = line.split(' --> ')
				start, end = map(parse_time, (start, end))
				start, end = map(shift_time, (start, end))
				out = '%s:%s:%s,%s --> %s:%s:%s,%s\n' % (
					str(start[0]).rjust(2, '0'),
					str(start[1]).rjust(2, '0'),
					str(start[2]).rjust(2, '0'),
					str(start[3]).rjust(3, '0'),
          
					str(end[0]).rjust(2, '0'),
					str(end[1]).rjust(2, '0'),
					str(end[2]).rjust(2, '0'),
					str(end[3]).rjust(3, '0'))
				sys.stdout.write(out)
			else:
				sys.stdout.write(line)

	def convert_vtt(self, srt_file):
		vtt_dest = os.path.splitext(srt_file)[0]+'.vtt'
		parser(srt_file, vtt_dest)

		return vtt_dest

