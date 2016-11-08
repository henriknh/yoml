import urllib2
import logging
import json
import thread
import threading
import urllib

#	MOVIES
#		https://yts.ag/api#list_movies
#	TV SHOWS
#		http://torrentproject.se/api
#	https://torrentapi.org/apidocs_v2.txt

class TorrentAPI():

	token = ''
	url = 'https://torrentapi.org/pubapi_v2.php'
	api_queue = []

	def __init__(self, torrent, database):
		self.torrent = torrent
		self.database = database

		thread.start_new_thread(self.fire_api_request,())

	def get_token(self):
		file = urllib2.urlopen(self.url + '?get_token=get_token')
		data = file.read()
		file.close()
		self.token = json.loads(data)['token']

	def error(self, data):
		try:
			json_data = json.loads(data)
			error_code = json_data['error_code']
			if error_code == 4 or error_code == 2:
				logging.error('Torrent API error 2 or 4: ' + str(json_data))
				self.get_token()
			else:
				logging.error('Torrent API error: ' + str(json_data))
			return error_code
		except KeyError:
			return None

	def fire_api_request(self):

		if not self.api_queue:
			threading.Timer(2.0, self.fire_api_request).start()
			return

		query_data = self.api_queue.pop(0)

		if query_data[0] == 'tvshow':
			tvshow_id = query_data[2]
			for rs in self.database.execute("SELECT Count(*) FROM tvshow WHERE tvshow_id=?", [tvshow_id]):
				if rs[0] == 0:
					return

		logging.info(query_data[1] + '&token=' + str(self.token))

		file = urllib2.urlopen(query_data[1] + '&token=' + str(self.token))
		data = file.read()
		file.close()
		
		json_data = json.loads(data)

		# Check for error
		try:
			error_code = json_data['error_code']
			if error_code == 4 or error_code == 2:
				logging.error('Torrent API error 2 or 4 (token): ' + str(json_data))
				self.get_token()
				self.api_queue.insert(0, query_data)

			elif error_code == 20:
				logging.error('Torrent API error 20 (no result): ' + str(json_data))

			elif error_code == 8:
				logging.error('Cant find search_tvdb in database: ' + str(json_data))
				new_query_data = query_data[1].split('&')[0]

				for part in query_data[1].split('&')[1:]:
					#logging.info(part)
					if 'search_tvdb=' in part:
						tvshow_id = part.replace('search_tvdb=','')
						#logging.info(tvshow_id)
					elif 'search_string=' in part:
						for rs in self.database.execute('SELECT SeriesName FROM tvshow WHERE tvshow_id=?', [tvshow_id]):
							SeriesName = urllib.quote_plus(str(rs[0] + ' '))
						#logging.info(SeriesName)
						new_part = part.replace('search_string=', 'search_string=' + SeriesName)
						new_query_data += '&' + new_part
					else:
						new_query_data += '&' + part

				query_data[1] = new_query_data
				self.api_queue.insert(0, query_data)

			#else:
			#	self.api_queue.insert(0, query_data)

		except KeyError:
			# No error
			self.handle_api_result(query_data, json_data)

		threading.Timer(2.0, self.fire_api_request).start()

	def queue_tvshow_torrent_search(self, tvshow_id, SeriesName, episode_id, episode, absolute):

		for rs in self.database.execute("SELECT * FROM config WHERE config LIKE 'torrent_%'", None):
			if(rs[1] == 'torrent_prefered_quality'):
				torrent_prefered_quality = map(str.strip, str(rs[3]).split(','))
			if(rs[1] == 'torrent_ignore_words'):
				torrent_ignore_words = rs[3]
			if(rs[1] == 'torrent_min_seeders'):
				torrent_min_seeders = rs[3]
			if(rs[1] == 'torrent_min_leechers'):
				torrent_min_leechers = rs[3]
			if(rs[1] == 'torrent_verified_uploaders'):
				torrent_verified_uploaders = rs[3]

		for rs in self.database.execute('SELECT Count(*) FROM downloading WHERE episode_id=?', [episode_id]):
			if rs[0] != 0:
				return

		for quality in torrent_prefered_quality:
			query = self.url + '?mode=search&search_tvdb=' + str(tvshow_id) + '&search_string=' + urllib.quote_plus(str(episode) + ' ' + str(quality)) + '&sort=seeders&min_seeders=' + str(torrent_min_seeders) + '&min_leechers=' + str(torrent_min_leechers) + '&ranked=' + torrent_verified_uploaders
			self.api_queue.append(['tvshow', query, tvshow_id, episode_id])
			if absolute != None:
				query = self.url + '?mode=search&search_tvdb=' + str(tvshow_id) + '&search_string=' + urllib.quote_plus(str(absolute) + ' ' + str(quality)) + '&sort=seeders&min_seeders=' + str(torrent_min_seeders) + '&min_leechers=' + str(torrent_min_leechers) + '&ranked=' + torrent_verified_uploaders
				self.api_queue.append(['tvshow', query, tvshow_id, episode_id])

		if len(torrent_prefered_quality) == 0:
			query = self.url + '?mode=search&search_tvdb=' + str(tvshow_id) + '&search_string=' + urllib.quote_plus(str(episode)) + '&sort=seeders&min_seeders=' + str(torrent_min_seeders) + '&min_leechers=' + str(torrent_min_leechers) + '&ranked=' + torrent_verified_uploaders
			self.api_queue.append(['tvshow', query, tvshow_id, episode_id])
			if absolute != None:
				query = self.url + '?mode=search&search_tvdb=' + str(tvshow_id) + '&search_string=' + urllib.quote_plus(str(absolute)) + '&sort=seeders&min_seeders=' + str(torrent_min_seeders) + '&min_leechers=' + str(torrent_min_leechers) + '&ranked=' + torrent_verified_uploaders
				self.api_queue.append(['tvshow', query, tvshow_id, episode_id])

	def handle_api_result(self, query_data, json_data):

		for rs in self.database.execute("SELECT value FROM config WHERE config='torrent_ignore_words'", None):
			torrent_ignore_words = map(str.strip, str(rs[0]).split(','))

		# query_data = ['tvshow', query, tvshow_id, episode_id]
		if query_data[0] == 'tvshow':

			filename = json_data['torrent_results'][0]['filename']
			download = json_data['torrent_results'][0]['download']

			for result in json_data['torrent_results']:

				filename = result['filename']
				download = result['download']

				# Check if ignore words exists
				if any(ext in filename for ext in torrent_ignore_words):
					continue

					
				# Check if episode is already downloading
				for rs in self.database.execute('SELECT Count(*) FROM downloading WHERE episode_id=?', [query_data[3]]):
					torrent_count = rs[0]

				# Add to database and torrent program
				if torrent_count == 0:
					#add to torrent program
					logging.info('add_torrent ' + filename)
					hashString = self.torrent.add_torrent(download)
					if hashString != None:
						self.database.execute('INSERT INTO downloading (tvshow_id, episode_id, download, hashString) VALUES (?,?,?,?)', [query_data[2], query_data[3], download, hashString])
					
				break

		# query_data = ['movie', query, movie_id]
		if query_data[0] == 'movie':
			print ' handle api result, for movie XD'


