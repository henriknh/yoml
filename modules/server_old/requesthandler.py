import thread
import logging
import datetime

class RequestHandler():

	library = None

	def __init__(self, library, database):
		self.library = library
		self.database = database


	def handle_request(self, data):
		data = data.split(',')
		logging.debug("Request Handler recieved: %s", data)


		if data[0] == 'fullscan':

			thread.start_new_thread(self.library.scan_full, ())
			#return str(data[0] + u';;;;' + str(self.library.scan_full()))



		if data[0] == 'libraries':
			return str(data[0] + u';;;;' + self.library.get_libraries_as_string())



		if data[0] == 'tvshows':
			ret = ''
			for tvshow in self.database.execute('SELECT  `tvshow_id` FROM tvshow WHERE 1', None):
				for r in tvshow:
					ret += unicode(r) + u';; '


			return unicode(data[0] + u';;;;' + unicode(ret))



		if data[0] == 'tvshows_thumbnail_data':

			ret = ''

			tvshows = []

			for tvshow in self.database.execute("SELECT `tvshow_id` FROM tvshow WHERE 1 ORDER BY REPLACE(SeriesName, 'The ', '')", None):

				tvshows.append(tvshow[0])

			for tvshow in tvshows:
			
				for rs in self.database.execute('SELECT `tvshow_id`,`FirstAired`,`SeriesName`,`poster` FROM tvshow WHERE `tvshow_id`=?', [tvshow]):
					for r in rs:
						ret += unicode(r) + u';; '

				nr_of_progress = 0
				for rs in self.database.execute('SELECT `progress`,`watched` FROM progress WHERE `tvshow_id`=?', [tvshow]):
					if rs[0] != 0 or rs[1] != 0:
						nr_of_progress += 1

				nr_of_episodes = 0
				nr_of_not_downloaded = 0
				for rs in self.database.execute('SELECT `path`,`FirstAired` FROM episode WHERE `seriesid`=?', [tvshow]):
					if rs[0] != '':
						nr_of_episodes += 1
					if rs[0] == '' and rs[1] != '':
						
						date1 = datetime.datetime.now().date()
						date2 = datetime.datetime.strptime(rs[1], "%Y-%m-%d").date()

						if date1 > date2:
							nr_of_not_downloaded += 1

				ret += unicode(nr_of_episodes - nr_of_progress) + u';; ' + unicode(nr_of_not_downloaded) + u';; '



			for fanart in self.database.execute('SELECT `fanart` FROM tvshow ORDER BY RANDOM() LIMIT 1', None):
				ret += unicode(fanart[0]) + u';; '


			return unicode(data[0] + u';;;;' + unicode(ret))



		if data[0] == 'tvshow':
			ret = ''
			for rs in self.database.execute('SELECT * FROM tvshow WHERE `tvshow_id`=?', data[1].split(',')):
				for r in rs:
					ret += unicode(r) + u';; '
			return unicode(data[0] + u';;;;' + unicode(ret))



		if data[0] == 'episodes':
			episode_arr = []
			episode_id_arr = []
			for tvshow in self.database.execute('SELECT  * FROM episode WHERE `seriesid`=?', data[1].split(',')):
				temp = ''
				for r in tvshow:
					temp += unicode(r) + u';; '
				episode_arr.append(unicode(temp))
				episode_id_arr.append(str(tvshow[0]))

			for index, episode_id in enumerate(episode_id_arr):
				progress = self.library.get_episode_progress('1', str(episode_id))
				if progress == '':
					episode_arr[index] += ';; ;; '
				else:
					episode_arr[index] += progress

			ret = ''
			for arr in episode_arr:
				ret += arr;

			return unicode(data[0] + u';;;;' + unicode(ret))

		return '0'