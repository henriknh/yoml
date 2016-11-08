from directorywatcher import *
from modules.util.util import *
from thetvdb import *
import logging
import datetime
import thread
import threading
import os
import shutil
import json
import random
from random import randint

class Library():

	tvdb = TheTVDB()

	dataDir = ''

	def __init__(self, dataDir, database, ffmpeg, torrent, torrentapi):
		self.database = database
		self.dataDir = dataDir
		self.ffmpeg = ffmpeg
		self.torrent = torrent
		self.torrentapi = torrentapi

		if not os.path.exists(dataDir):
			os.makedirs(dataDir)
		if not os.path.exists(dataDir + '/' + 'tvshows'):
			os.makedirs(dataDir + '/' + 'tvshows')
		if not os.path.exists(dataDir + '/' + 'movies'):
			os.makedirs(dataDir + '/' + 'movies')
		if not os.path.exists(dataDir + '/' + 'pictures'):
			os.makedirs(dataDir + '/' + 'pictures')
		if not os.path.exists(dataDir + '/' + 'music'):
			os.makedirs(dataDir + '/' + 'music')

		# This is a throwaway variable to deal with a python bug
		throwaway = datetime.datetime.strptime('20110101','%Y%m%d')

		thread.start_new_thread(self.update_libraries_variable,())
		thread.start_new_thread(self.search_missing_media_timer,())

		# Start watcher in dirs
		#watcher = DirectoryWatcher()
		#for libary in self.libraries:
		#    watcher.add_watch(libary)
		##########watcher.start()
		#thread.start_new_thread(watcher.start, ())

	def update_libraries_variable(self):

		temp = []

		for rs in self.database.execute('SELECT * FROM library WHERE 1', None):

			library = {}

			library['library_id']   = rs[0]
			library['type'] = rs[1]
			library['path'] = rs[2]

			temp.append(library)

		self.libraries = temp
		temp = None

	def new_library(self, library_type, path):
		self.database.execute('INSERT INTO library (`type`, `path`) VALUES (?, ?)', [library_type, path])
		self.update_libraries_variable()
		for library in self.libraries:
			if library['path'] == path:
				self.scan_library(library)
				self.search_missing_media(library['library_id'])

	
	def get_libraries_xml(self):

		xml = '<?xml version="1.0" encoding="UTF-8"?>'

		xml += '<libraries>'

		for library in self.libraries:

			xml += '<library>'
			xml += '<library_id>' + str(library['library_id']) + '</library_id>'
			xml += '<type>' + str(library['type']) + '</type>'
			xml += '<path>' + str(library['path']) + '</path>'
			xml += '</library>'

		xml += '</libraries>'

		return xml
	

	def scan_full(self):

		if self.libraries is None:
			logging.info('Scan could not start. No library.')
			return

		logging.info('Fullscan started')


		for library in self.libraries:
			self.scan_library(library)
						
		logging.info("Fullscan completed")
		
		return 1
	def scan_library(self, library):

		extensions = None
		if library['type'] == 'tvshows' or library['type'] == 'movies':
			extensions = extensions_videos
		if library['type'] == 'pictures':
			extensions = extensions_pictures
		if library['type'] == 'music':
			extensions = extensions_music

		# tvshows
		if library['type'] == 'tvshows':
			for tvshow in os.listdir(library['path']):
				self.scan_tvshow(str(library['library_id']), tvshow, library['path'] + '/' + tvshow)
						
		# movies
		if library['type'] == 'movies':
			x=1

		# pictures
		if library['type'] == 'pictures':
			x=2

		# music
		if library['type'] == 'music':
			x=3

	def scan_tvshow(self, library_id, tvshow, path):
		logging.info("Scanning TV Show: %s" % tvshow)

		destination = os.path.join(self.dataDir + '/tvshows/' + tvshow)

		logging.info(destination)

		# Get tv show data
		seriesid = self.tvdb.get_tvshow_seriesid(tvshow)
		self.tvdb.download_tvshow_data(seriesid, destination)
		self.tvdb.get_tvshow_data(library_id, seriesid, destination, path, self.database)
		self.tvdb.get_episode_data(library_id, seriesid, destination, path, self.database)

		self.search_missing_media_tvshow(tvshow, seriesid)

	def get_episode_progress(self, user_id, episode_id):

		retval = []

		for rs in self.database.execute('SELECT `progress`, `watched` FROM progress WHERE `user_id`=? AND `episode_id`=?', [user_id, episode_id]):

			if rs[0] == '':
				retval.append('0')
			else:
				retval.append(rs[0])

			if rs[1] == '':
				retval.append('0')
			else:
				retval.append(rs[1])

		if retval == []:
			return [0, 0]

		return retval

	def get_tvshows(self):

		logging.info("Fetching data for TV Shows")

		tvshows = []
		rs_tvshows = []

		
		for rs_tvshows_temp in self.database.execute("SELECT `tvshow_id`,`FirstAired`,`SeriesName`,`poster` FROM tvshow WHERE 1 ORDER BY REPLACE(SeriesName, 'The ', '')", None):
			rs_tvshows.append(rs_tvshows_temp)
		
		for rs_tvshow in rs_tvshows:
			tvshow = {}

			tvshow['tvshow_id'] = rs_tvshow[0]
			tvshow['FirstAired'] = rs_tvshow[1]
			tvshow['SeriesName'] = rs_tvshow[2]
			tvshow['poster'] = "{0}{2}.{1}".format(*rs_tvshow[3].rsplit('.', 1) + ['-thumb'])

			nr_of_progress = 0
			for rs in self.database.execute('SELECT `progress`,`watched` FROM progress WHERE `tvshow_id`=?', [tvshow['tvshow_id']]):
				if rs[0] != 0 or rs[1] != 0:
					nr_of_progress += 1

			nr_of_episodes = 0
			nr_of_not_downloaded = 0
			data = []
			for rs in self.database.execute('SELECT `path`,`FirstAired` FROM episode WHERE `seriesid`=?', [tvshow['tvshow_id']]):
				data.append((rs[0],rs[1]))

			for path, FirstAired in data:
				if FirstAired != '' and FirstAired != None:

					date1 = datetime.datetime.now().date()
					date2 = datetime.datetime.strptime(FirstAired, "%Y-%m-%d").date()

					if date1 > date2:
						nr_of_episodes += 1

					if path == '' and FirstAired != '':

						if date1 > date2:
							nr_of_not_downloaded += 1

			tvshow['unwatched'] = nr_of_episodes - nr_of_progress
			tvshow['undownloaded'] = nr_of_not_downloaded

			for downloading in self.database.execute("SELECT Count(*) FROM downloading WHERE tvshow_id=?", [tvshow['tvshow_id']]):
				tvshow['downloading'] = downloading[0]

			tvshows.append(tvshow)

		return tvshows

	def get_tvshow(self, tvshow_id):

		logging.info("Fetching data for TV Show: %s" % tvshow_id)

		tvshow = {}

		for rs_tvshow in self.database.execute('SELECT * FROM tvshow WHERE `tvshow_id`=?', [tvshow_id]):

			tvshow['tvshow_id'] = rs_tvshow[0]
			tvshow['library_id'] = rs_tvshow[1]
			tvshow['Actors'] = rs_tvshow[2]
			tvshow['ContentRating'] = rs_tvshow[3]
			tvshow['FirstAired'] = rs_tvshow[4]
			tvshow['Genre'] = rs_tvshow[5]
			tvshow['IMDB_ID'] = rs_tvshow[6]
			tvshow['Network'] = rs_tvshow[7]
			tvshow['Overview'] = rs_tvshow[8]
			tvshow['Rating'] = rs_tvshow[9]
			tvshow['Runtime'] = rs_tvshow[10]
			tvshow['SeriesName'] = rs_tvshow[11]
			tvshow['Status'] = rs_tvshow[12]
			tvshow['banner'] = rs_tvshow[13]
			tvshow['fanart'] = rs_tvshow[14]
			tvshow['poster'] = rs_tvshow[15]
			tvshow['path'] = rs_tvshow[16]
			tvshow['watched'] = self.all_downloaded_watched(tvshow_id)

		episodes = []
		episodes_temp = []

		for rs_episodes_temp in self.database.execute('SELECT * FROM episode WHERE `seriesid`=?', [tvshow_id]):
			episodes_temp.append(rs_episodes_temp)

		for rs_episodes in episodes_temp:

			episode = {}

			episode['episode_id'] = rs_episodes[0]
			episode['library_id'] = rs_episodes[1]
			episode['Director'] = rs_episodes[2]
			episode['EpisodeName'] = rs_episodes[3]
			episode['EpisodeNumber'] = rs_episodes[4]
			episode['FirstAired'] = rs_episodes[5]
			episode['Overview'] = rs_episodes[6]
			episode['Rating'] = rs_episodes[7]
			episode['SeasonNumber'] = rs_episodes[8]
			episode['Writer'] = rs_episodes[9]
			episode['absolute_number'] = rs_episodes[10]
			episode['filename'] = rs_episodes[11]
			episode['seriesid'] = rs_episodes[12]
			episode['path'] = rs_episodes[13]

			if episode['FirstAired'] == '':
				continue
			date1 = datetime.datetime.now().date()
			date2 = datetime.datetime.strptime(episode['FirstAired'], "%Y-%m-%d").date()
			if date1 < date2:
				#continue
				pass

			user_id = 0
			progress = self.get_episode_progress(user_id, str(rs_episodes[0]))
						
			episode['progress'] = progress[0]
			episode['watched'] = progress[1]

			for downloading in self.database.execute('SELECT Count(*) FROM downloading WHERE episode_id=?', [episode['episode_id']]):
				if downloading[0] == 0:
					episode['downloading'] = 0
				else:
					episode['downloading'] = 1

			episodes.append(episode)


		return tvshow, episodes

	def get_progressed_media(self):

		logging.info('get_progressed_media')

		media = []

		progress_temp = []

		for rs_temp in self.database.execute('SELECT * FROM progress WHERE `progress`!=0', None):
			progress_temp.append(rs_temp)

		for progress_item in progress_temp:

			if progress_item[4] != '':

				#
				#   Handle Movie
				#
				print 'get_progressed_media, movie'

			if progress_item[2] != '' and progress_item[3] != '':

				#
				#   Handle TV Show episode
				#
				
				for rs_episodes in self.database.execute('SELECT * FROM episode WHERE `episode_id`=?', [progress_item[3]]):

					item = {}

					item['type'] = 'episode'
					item['episode_id'] = rs_episodes[0]
					item['library_id'] = rs_episodes[1]
					item['Director'] = rs_episodes[2]
					item['EpisodeName'] = rs_episodes[3]
					item['EpisodeNumber'] = rs_episodes[4]
					item['FirstAired'] = rs_episodes[5]
					item['Overview'] = rs_episodes[6]
					item['Rating'] = rs_episodes[7]
					item['SeasonNumber'] = rs_episodes[8]
					item['Writer'] = rs_episodes[9]
					item['absolute_number'] = rs_episodes[10]
					item['filename'] = rs_episodes[11]
					item['seriesid'] = rs_episodes[12]
					item['path'] = rs_episodes[13]

					for rs_tvshow in self.database.execute('SELECT SeriesName FROM tvshow WHERE tvshow_id=?', [item['seriesid']]):
						item['SeriesName'] = rs_tvshow[0]

					if item['FirstAired'] == '':
						continue
					date1 = datetime.datetime.now().date()
					date2 = datetime.datetime.strptime(item['FirstAired'], "%Y-%m-%d").date()
					if date1 < date2:
						continue

					user_id = 0
					progress = self.get_episode_progress(user_id, str(rs_episodes[0]))
								
					item['progress'] = progress[0]
					item['watched'] = progress[1]

					for downloading in self.database.execute("SELECT Count(*) FROM downloading WHERE episode_id=?", [item['episode_id']]):
						item['downloading'] = downloading[0]

					media.append(item)

		for rs in self.database.execute('SELECT tvshow_id FROM tvshow WHERE 1', None):
			tvshow_id = rs[0]
			next_not_watched_episode = False
			offset = 0

			for rs2 in self.database.execute('SELECT episode_id FROM episode WHERE seriesid=?', [tvshow_id]):
				if next_not_watched_episode:
					break
				episode_id = rs2[0]
				offset = offset + 1
				for rs3 in self.database.execute('SELECT COUNT(*) FROM progress WHERE episode_id=? AND watched="1"', [episode_id]):
					if next_not_watched_episode:
						break
					if rs3[0] == 0:
						next_not_watched_episode = True


			for rs_episodes in self.database.execute('SELECT * FROM episode WHERE episode_id=?', [episode_id]):

				item = {}

				item['type'] = 'episode'
				item['episode_id'] = rs_episodes[0]
				item['library_id'] = rs_episodes[1]
				item['Director'] = rs_episodes[2]
				item['EpisodeName'] = rs_episodes[3]
				item['EpisodeNumber'] = rs_episodes[4]
				item['FirstAired'] = rs_episodes[5]
				item['Overview'] = rs_episodes[6]
				item['Rating'] = rs_episodes[7]
				item['SeasonNumber'] = rs_episodes[8]
				item['Writer'] = rs_episodes[9]
				item['absolute_number'] = rs_episodes[10]
				item['filename'] = rs_episodes[11]
				item['seriesid'] = rs_episodes[12]
				item['path'] = rs_episodes[13]

				if item['absolute_number'] == 1:
					continue

				# tvshow allready in dash page, ignore
				tvshow_exists_on_dash = False
				for media_item in media:
					logging.info(media_item['seriesid'])
					logging.info(item['seriesid'])
					logging.info('')
					if media_item['seriesid'] == item['seriesid']:
						tvshow_exists_on_dash = True
				if tvshow_exists_on_dash:
					continue

				for rs_tvshow in self.database.execute('SELECT SeriesName FROM tvshow WHERE tvshow_id=?', [tvshow_id]):
					item['SeriesName'] = rs_tvshow[0]

				if item['FirstAired'] == '':
					continue
				date1 = datetime.datetime.now().date()
				date2 = datetime.datetime.strptime(item['FirstAired'], "%Y-%m-%d").date()
				if date1 < date2:
					continue

				user_id = 0
				progress = self.get_episode_progress(user_id, str(rs_episodes[0]))
								
				item['progress'] = progress[0]
				item['watched'] = progress[1]

				for downloading in self.database.execute("SELECT Count(*) FROM downloading WHERE episode_id=?", [item['episode_id']]):
					item['downloading'] = downloading[0]

				media.append(item)

		return media

	def get_data_episode(self, tvshow_id, episode_id):

		logging.info("Fetching player data for episode: %(episode)s in tvshow: %(tvshow)s" % {"episode" : episode_id, "tvshow" : tvshow_id})

		temp = []

		tvshow = {}
		temp = []
		for rs in self.database.execute('SELECT * FROM tvshow WHERE `tvshow_id`=?', [tvshow_id]):
			temp.append(rs)

		for rs_tvshow in temp:

			tvshow['tvshow_id'] = rs_tvshow[0]
			tvshow['library_id'] = rs_tvshow[1]
			tvshow['Actors'] = rs_tvshow[2]
			tvshow['ContentRating'] = rs_tvshow[3]
			tvshow['FirstAired'] = rs_tvshow[4]
			tvshow['Genre'] = rs_tvshow[5]
			tvshow['IMDB_ID'] = rs_tvshow[6]
			tvshow['Network'] = rs_tvshow[7]
			tvshow['Overview'] = rs_tvshow[8]
			tvshow['Rating'] = rs_tvshow[9]
			tvshow['Runtime'] = rs_tvshow[10]
			tvshow['SeriesName'] = rs_tvshow[11]
			tvshow['Status'] = rs_tvshow[12]
			tvshow['banner'] = rs_tvshow[13]
			tvshow['fanart'] = rs_tvshow[14]
			tvshow['poster'] = rs_tvshow[15]
			tvshow['path'] = rs_tvshow[16]

		episode = {}

		temp = []
		for rs in self.database.execute('SELECT * FROM episode WHERE `episode_id`=?', [episode_id]):
			temp.append(rs)

		for rs_episodes in temp:     

			episode['episode_id'] = rs_episodes[0]
			episode['library_id'] = rs_episodes[1]
			episode['Director'] = rs_episodes[2]
			episode['EpisodeName'] = rs_episodes[3]
			episode['EpisodeNumber'] = rs_episodes[4]
			episode['FirstAired'] = rs_episodes[5]
			episode['Overview'] = rs_episodes[6]
			episode['Rating'] = rs_episodes[7]
			episode['SeasonNumber'] = rs_episodes[8]
			episode['Writer'] = rs_episodes[9]
			episode['absolute_number'] = rs_episodes[10]
			episode['filename'] = rs_episodes[11]
			episode['seriesid'] = rs_episodes[12]
			episode['path'] = rs_episodes[13]

			for count in self.database.execute('SELECT Count(*) FROM progress WHERE episode_id=?', [episode_id]):
				if count[0] == 0:
					logging.info('count == 0')
					episode['watched'] = 0
				else:
					logging.info('count != 0')
					for watched in self.database.execute('SELECT watched FROM progress WHERE episode_id=?', [episode_id]):
						episode['watched'] = watched[0]
						logging.info(episode['watched'])

		return [tvshow, episode]

	def get_data_episode_player(self, tvshow_id, episode_id):

		logging.info("Fetching player data for episode: %(episode)s in tvshow: %(tvshow)s" % {"episode" : episode_id, "tvshow" : tvshow_id})

		temp = []

		tvshow = {}
		temp = []
		for rs in self.database.execute('SELECT * FROM tvshow WHERE `tvshow_id`=?', [tvshow_id]):
			temp.append(rs)

		for rs_tvshow in temp:

			tvshow['tvshow_id'] = rs_tvshow[0]
			tvshow['library_id'] = rs_tvshow[1]
			tvshow['Actors'] = rs_tvshow[2]
			tvshow['ContentRating'] = rs_tvshow[3]
			tvshow['FirstAired'] = rs_tvshow[4]
			tvshow['Genre'] = rs_tvshow[5]
			tvshow['IMDB_ID'] = rs_tvshow[6]
			tvshow['Network'] = rs_tvshow[7]
			tvshow['Overview'] = rs_tvshow[8]
			tvshow['Rating'] = rs_tvshow[9]
			tvshow['Runtime'] = rs_tvshow[10]
			tvshow['SeriesName'] = rs_tvshow[11]
			tvshow['Status'] = rs_tvshow[12]
			tvshow['banner'] = rs_tvshow[13]
			tvshow['fanart'] = rs_tvshow[14]
			tvshow['poster'] = rs_tvshow[15]
			tvshow['path'] = rs_tvshow[16]

		episode = {}
		videoinfo = {}

		temp = []
		for rs in self.database.execute('SELECT * FROM episode WHERE `episode_id`=?', [episode_id]):
			temp.append(rs)

		for rs_episodes in temp:     

			episode['episode_id'] = rs_episodes[0]
			episode['library_id'] = rs_episodes[1]
			episode['Director'] = rs_episodes[2]
			episode['EpisodeName'] = rs_episodes[3]
			episode['EpisodeNumber'] = rs_episodes[4]
			episode['FirstAired'] = rs_episodes[5]
			episode['Overview'] = rs_episodes[6]
			episode['Rating'] = rs_episodes[7]
			episode['SeasonNumber'] = rs_episodes[8]
			episode['Writer'] = rs_episodes[9]
			episode['absolute_number'] = rs_episodes[10]
			episode['filename'] = rs_episodes[11]
			episode['seriesid'] = rs_episodes[12]
			episode['path'] = rs_episodes[13]

			videoinfo['m3u8'] = self.ffmpeg.run_ffmpeg(episode['path'])
			videoinfo['start_position'] = 0
			videoinfo['duration'] = self.ffmpeg.duration(episode['path'])

		return [tvshow, episode, videoinfo]

	def get_random_tvshow_fanart(self):
		for rs in self.database.execute('SELECT `fanart` FROM tvshow ORDER BY RANDOM() LIMIT 1', None):
			return rs[0]
		return ''

	def get_manage_media(self):
		data = []

		for rs in self.database.execute('SELECT * FROM library WHERE 1 ORDER BY `type` ASC', None):
			library = {}
			library['library_id'] = str(rs[0])
			library['library_type'] = str(rs[1])
			library['library_path'] = str(rs[2])
			data.append(library)
		
		return data

	def remove_library(self, id):
		self.database.execute('DELETE FROM library WHERE `library_id`=?', [id])
		self.database.execute('DELETE FROM episode WHERE `library_id`=?', [id])
		self.database.execute('DELETE FROM tvshow WHERE `library_id`=?', [id])

		self.update_libraries_variable();

	def get_statistics(self):
		data = {}

		# TV Shows
		for rs in self.database.execute('SELECT Count(*) FROM tvshow', None):
			data['tvshows_tvshows'] = rs[0]

		for rs in self.database.execute('SELECT Count(*) FROM episode', None):
			data['tvshows_episodes'] = rs[0]

		for rs in self.database.execute('SELECT Count(*) FROM progress WHERE `watched`=1 AND `episode_id` IS NOT NULL', None):
			data['tvshows_seen'] = rs[0]

		return data

	def new_media(self, type, media, library_id):

		if type == 'tvshow':
			seriesid = media

			tvshow = self.tvdb.get_tvshow_name(seriesid)

			for rs in self.database.execute('SELECT `path` FROM library WHERE `library_id`=?', [library_id]):
				path = rs[0] + '/' + tvshow

			self.scan_tvshow(library_id, tvshow, path)
			self.search_missing_media()

		if type == 'movie':
			a = 1

	def search_missing_media_timer(self):
		for rs in self.database.execute("SELECT value FROM config WHERE config='torrent_search_missing_media'", None):
			torrent_search_missing_media = rs[0]
		
		self.search_missing_media()

		threading.Timer(float(torrent_search_missing_media)*3600 + randint(0,59)*60, self.search_missing_media_timer).start()

	def search_missing_media(self, library_id=None):

		logging.info('Search missing media')

		if library_id == None:
			sql = 'SELECT SeriesName, tvshow_id FROM tvshow WHERE 1'
			data = None
		else:
			sql = 'SELECT SeriesName, tvshow_id FROM tvshow WHERE library_id=?'
			data = [library_id]

		
		for rs in self.database.execute(sql, data):
			self.search_missing_media_tvshow(rs[0], rs[1])
			
		return

	def search_missing_media_tvshow(self, SeriesName, tvshow_id):

		current_season = 1
		episodes_in_season = 0
		missing_episodes_in_season = 0

		for rs in self.database.execute("SELECT * FROM episode WHERE seriesid=? AND FirstAired IS NOT '' ORDER BY SeasonNumber ASC", [tvshow_id]):

			episode_id = rs[0]
			EpisodeNumber = rs[4]
			FirstAired = rs[5]
			SeasonNumber = rs[8]
			absolute_number = rs[10]
			path = rs[13]


			FirstAired = datetime.datetime.strptime(FirstAired, "%Y-%m-%d")
			if FirstAired > datetime.datetime.now():
				continue

			if path == '':

				# S01E01 E02 / S01E01E02
				if absolute_number == 1:
					episode = ('S%02dE%02d E%02d' % (int(SeasonNumber), int(EpisodeNumber), int(EpisodeNumber)+1))
					self.torrentapi.queue_tvshow_torrent_search(tvshow_id, SeriesName, episode_id, episode, None)
					
				episode = ('S%02dE%02d' % (int(SeasonNumber), int(EpisodeNumber)))
			
				if absolute_number == '':
					self.torrentapi.queue_tvshow_torrent_search(tvshow_id, SeriesName, episode_id, episode, None)
				else:
					absolute = ('E%02d' % int(absolute_number))
					self.torrentapi.queue_tvshow_torrent_search(tvshow_id, SeriesName, episode_id, episode, absolute)

		return

	def refresh_media(self, type, id):
		logging.info('refresh_media ' + str(type) + ' ' + str(id))

		if type == 'tvshow':
			for rs in self.database.execute('SELECT library_id, SeriesName, path FROM tvshow WHERE tvshow_id=?', [id]):
				self.scan_tvshow(rs[0], rs[1], rs[2])
		if type == 'episode':
			# Fix so only for episode
			logging.info('Fix so only for episode')
			for rs in self.database.execute('SELECT seriesid FROM episode WHERE episode_id=?', [id]):
				tvshow_id = rs[0]
				for rs2 in self.database.execute('SELECT library_id, SeriesName, path FROM tvshow WHERE tvshow_id=?', [tvshow_id]):
					self.scan_tvshow(rs2[0], rs2[1], rs2[2])

		if type == 'movie':
			pass
		if type == 'picture':
			pass
		return

	def toggle_media_watched(self, type, id, watched):
		logging.info('toggle_media_watched ' + str(type) + ' ' + str(id) + ' ' + str(watched))

		if type == 'tvshow':
			data = []

			for rs in self.database.execute("SELECT episode_id, FirstAired FROM episode WHERE seriesid=? AND path IS NOT ''", [id]):
				data.append((rs[0], rs[1]))

			for episode_id, FirstAired in data:
				user_id = '0'
				logging.info(episode_id)

				FirstAired = datetime.datetime.strptime(FirstAired, "%Y-%m-%d")
				if FirstAired > datetime.datetime.now():
					continue

				if watched == 1:
					progress = 0
				else:
					for rs_progress in self.database.execute('SELECT progress FROM progress WHERE episode_id=?', [episode_id]):
						progress = rs_progress[0]
				
				self.database.execute("INSERT OR REPLACE INTO progress (progress_id, user_id, tvshow_id, episode_id, progress, watched) values ((SELECT progress_id FROM progress WHERE episode_id=?), ?, ?, ?, ?, ?);", [episode_id, user_id, id, episode_id, progress, watched])
		if type == 'episode':
			for rs in self.database.execute('SELECT seriesid FROM episode WHERE episode_id=?', [id]):
				tvshow_id = rs[0]
				user_id = '0'

				if watched == 1:
					progress = 0
				else:
					for rs_progress in self.database.execute('SELECT progress FROM progress WHERE episode_id=?', [id]):
						progress = rs_progress[0]

				self.database.execute("INSERT OR REPLACE INTO progress (progress_id, user_id, tvshow_id, episode_id, progress, watched) values ((SELECT progress_id FROM progress WHERE episode_id=?), ?, ?, ?, ?, ?);", [id, user_id, tvshow_id, id, progress, watched])
		if type == 'movie':
			pass
		if type == 'picture':
			pass
		return

	def remove_media(self, type, id):
		logging.info('remove_media ' + str(type) + ' ' + str(id))

		dir = os.getcwd() + '/www/static/banners/'

		if type == 'tvshow':

			logging.info('1')

			for rs in self.database.execute('SELECT fanart, poster, path FROM tvshow WHERE tvshow_id=?', [id]):

				logging.info('2.1')
				logging.info('2.2')
				logging.info('2.3')

				fanart = rs[0]
				poster = rs[1]
				path = rs[2]
				logging.info('3')

				try:
					logging.info('4')
					if fanart != None:
						os.remove(dir + fanart)
					logging.info('5')
					if poster != None:
						os.remove(dir + poster)
						os.remove(dir + "{0}-{2}.{1}".format(*poster.rsplit('.', 1) + ['thumb']))
					
					logging.info('6')
					logging.info('7')
				except OSError:
					logging.info('Problem removing posters ' + str(type) + ' ' + str(id))
					pass

				logging.info('8')
				try:
					shutil.rmtree(path)
				except OSError:
					logging.info('Problem removing ' + str(type) + ' ' + str(id))
					pass

			logging.info('9.1')

			self.database.execute('DELETE FROM tvshow WHERE tvshow_id=?', [id])
			self.database.execute('DELETE FROM episode WHERE seriesid=?', [id])
			logging.info('9.2')
			try:
				shutil.rmtree(dir + 'episodes/' + str(id))
			except OSError:
				logging.info('Problem removing data ' + str(type) + ' ' + str(id))
				pass
			logging.info('10')
			
			torrent_hashStrings = []
			for rs in self.database.execute('SELECT hashString FROM downloading WHERE tvshow_id=?', [id]):
				torrent_hashStrings.append(rs[0])
			logging.info('11')
			for torrent_hashString in torrent_hashStrings:
				self.torrent.remove_torrent(torrent_hashString)
			logging.info('12')

		if type == 'episode':
			for rs in self.database.execute('SELECT path FROM episode WHERE episode_id=?', [id]):
				try:
					logging.info(rs[0])
					os.remove(rs[0])
					#shutil.rmtree(rs[0])
				except OSError:
					logging.info('Problem removing ' + str(type) + ' ' + str(id))
					pass
				self.database.execute("UPDATE episode SET path='' WHERE episode_id=?;", [id])

			torrent_hashStrings = []
			for rs in self.database.execute('SELECT hashString FROM downloading WHERE episode_id=?', [id]):
				torrent_hashStrings.append(rs[0])
			for torrent_hashString in torrent_hashStrings:
				self.torrent.remove_torrent(torrent_hashString)

		if type == 'movie':
			pass
		if type == 'picture':
			pass

		return

	def search(self, query):

		data = []
		movies = []
		tvshows = []
		episodes = []
		pictures = []

		# movie
		data.append(movies)

		# tvshow
		for rs in self.database.execute("SELECT * FROM tvshow WHERE SeriesName LIKE '%"+query+"%'", None):
			tvshow = {}
			tvshow['tvshow_id'] = rs[0]
			tvshow['FirstAired'] = rs[4]
			tvshow['Rating'] = rs[9]
			tvshow['SeriesName'] = rs[11]
			tvshows.append(tvshow)
		data.append(tvshows)

		# episode
		for rs in self.database.execute("SELECT * FROM episode WHERE EpisodeName LIKE '%"+query+"%'", None):
			episode = {}
			episode['episode_id'] = rs[0]
			episode['EpisodeName'] = rs[3]
			episode['FirstAired'] = rs[5]
			episode['Rating'] = rs[7]
			episode['tvshow_id'] = rs[12]
			episodes.append(episode)
		data.append(episodes)

		# picture
		data.append(pictures)

		return json.dumps(data)
	def all_downloaded_watched(self, tvshow_id):

		data = []

		for rs in self.database.execute("SELECT episode_id, FirstAired FROM episode WHERE seriesid=? AND path IS NOT ''", [tvshow_id]):
			data.append((rs[0], rs[1]))

		for episode_id, FirstAired in data:

			FirstAired = datetime.datetime.strptime(FirstAired, "%Y-%m-%d")
			if FirstAired > datetime.datetime.now():
				continue

			for rs in self.database.execute("SELECT watched FROM progress WHERE episode_id=?", [episode_id]):
				if rs[0] == 0:
					return 0
		return 1