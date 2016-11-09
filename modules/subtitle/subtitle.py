from modules.util.util import *

from packages.opensubtitles.opensubtitles import OpenSubtitles
from packages.opensubtitles.utils import File
import logging, os, zipfile, fileinput, re, sys

PATH_SRT_SHIFT = 'packages\\srt_shift\\srt_shift.py'

class Subtitle():

	def __init__(self, username, password):

		reload(sys)
		sys.setdefaultencoding("utf-8")

		self.subtitle = OpenSubtitles()
		self.login(username, password)

	def login(self, username, password):
		logging.info('Login to OpenSubtitle')
		self.token = self.subtitle.login(username, password)
		logging.info("OpenSubtitle token: " + str(self.token))

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
		self.parser(srt_file, vtt_dest)

		return vtt_dest
	def parser(self, path_in, path_out):
		if not os.path.exists(path_in):
			sys.stderr.write('File does not exist! Please check the directory.\n')
			return False

		file = open(path_in, 'r')
		sbt_obj = file.read()

		first_line = sbt_obj[:10]
		file.close()
		if first_line.find('<SAMI>') != -1:
			smi_obj = sbt_obj
			# Match ms pair
			ms_chk = re.findall('(<sync start=\d+><p class=\w+>(\s|\S){3,255}?(\s))'\
				,smi_obj, flags=re.IGNORECASE)
			g = 0
			ms_list = []
			if ms_chk[g][0].find('&nbsp;') != -1:
				g += 1
			while g < len(ms_chk):
				if g != len(ms_chk) - 1:
					first = ms_chk[g][0].find('&nbsp;')
					second = ms_chk[g + 1][0].find('&nbsp;')
					if first == -1 and second != -1:
						first_search = re.search('=\d+',ms_chk[g][0])
						second_search = re.search('=\d+',ms_chk[g + 1][0])
						ms_list.append(first_search.group(0))
						ms_list.append(second_search.group(0))
						g += 2
					elif first == -1 and second == -1:
						first_search = re.search('=\d+',ms_chk[g][0])
						second_search = re.search('=\d+',ms_chk[g + 1][0])
						ms_list.append(first_search.group(0))
						ms_list.append(second_search.group(0))
						g += 1
				elif g == len(ms_chk) - 1:
					first_search = re.search('=\d+',ms_chk[g][0])
					ms_list.append(first_search.group(0))
					g += 1
			ms_list = [a.replace('=','') for a in ms_list]
			# Check if last subtitle has an end
			chk_pair = len(ms_list) % 2
			if chk_pair != 0:
				last_ms = ms_list[len(ms_list) - 1]
				last_ms = int(last_ms) + 2000
				ms_list.append(last_ms)
			# Convert ms into timestamp
			i = 0
			ts_list = []
			for ms_el in ms_list:
				ms_el = ms_list[i]
				ms_el = int(ms_el) + 4000
				hr = int(ms_el) // 3600000
				ms_el = int(ms_el) % 3600000
				mi = int(ms_el) // 60000
				ms_el = int(ms_el) % 60000
				s = int(ms_el) // 1000
				ms_el = int(ms_el) % 1000
				ms = int(ms_el)
				ts_el = '%02d:%02d:%02d.%03d' % (hr, mi, s, ms)
				ts_list.append(ts_el)
				i += 1
			# Add two timestamps to SubRip format (ts --> ts)
			start = 0
			end = 1
			converted_ts = []
			while end <= len(ts_list):
				ts_el = ts_list[start] + " --> " + ts_list[end]
				converted_ts.append(ts_el)
				start += 2
				end += 2
			content_ls = re.findall('(<p class=\w+>(\s|\S){1,}?<sync)'\
			, smi_obj, flags=re.IGNORECASE)
			break_point = smi_obj.rfind("<P")
			last_ct = smi_obj[break_point:]
			last_ct = re.sub('</body>','', last_ct, flags=re.IGNORECASE)
			last_ct = re.sub('</sami>','', last_ct, flags=re.IGNORECASE)
			content_ls.append(last_ct)
			qwe = 0
			converted_ct = []
			while qwe < len(content_ls):
				if qwe == len(content_ls) - 1:
					content_el = content_ls[qwe]
				else:
					content_el = content_ls[qwe][0]
				content_el = re.sub('\r\n', '', content_el)
				content_el = re.sub('\n', '', content_el)
				content_el = re.sub('<br>', '\n', content_el)
				content_el = re.sub('&nbsp;', '', content_el, flags=re.IGNORECASE)
				content_el = re.sub('<p class=\w+>', '', content_el, flags=re.IGNORECASE)
				content_el = re.sub('<sync','', content_el, flags=re.IGNORECASE)
				converted_ct.append(content_el)
				qwe += 1
			converted_ct = list(filter(bool, converted_ct))
			converted_ct = list(filter(lambda whitespace: whitespace.strip(), converted_ct))
			if len(converted_ts) != len(converted_ct):
				sys.stderr.write("The SAMI file has SYNC tag(s) with no actual caption!\nPlease check your SAMI file!\n")
				return False
			que = 1
			num = 0
			final_obj = "WEBVTT\n\n"
			while num < len(converted_ts):
				if que == len(converted_ts):
					final_obj = final_obj + str(que) +'\n' + converted_ts[num] + '\n' + converted_ct[num]
				else:
					final_obj = final_obj + str(que) +'\n' + converted_ts[num] + '\n' + converted_ct[num] + '\n\n'
				que += 1
				num += 1
			if sys.version_info <= (2,8):
				final_obj = unicode(final_obj).encode("utf-8")
			with open(path_out, "w") as converted:
				converted.write(final_obj)
			if converted:
				converted.close()
				print("Successfully converted the subtitle!")
		elif first_line[:5].find('1') != -1:
			srt_obj = sbt_obj
			# Convert the timestamp format
			org_ts = re.findall('(\d{0,2}?:\d{0,2}?:\d{0,2}?,)+', srt_obj)
			mod_ts = [a.replace(',','.') for a in org_ts]
			i = 0
			for org in org_ts:
				org = org_ts[i]
				mod = mod_ts[i]
				mod = mod[:-2] + str(int(mod[-2])) + "."
				srt_obj = re.sub(org, mod, srt_obj)
				i += 1
			# Add string "WEBVTT" at the top
			header = "WEBVTT\n\n"
			srt_obj = header + srt_obj
			if sys.version_info <= (2,8):
				srt_obj = unicode(srt_obj).decode("utf-8")
			with open(path_out, "wb") as converted:
				converted.write(srt_obj)
			if converted:
				converted.close()
				print("Successfully converted the subtitle!")
		else:
			print("The file is either corrupted or not a valid SAMI or SubRip file!")
