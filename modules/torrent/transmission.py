import logging
import requests
import os
import json
import shutil
from modules.util.util import *
from requests.auth import HTTPBasicAuth

# TR_STATUS_STOPPED        = 0, /* Torrent is stopped */
# TR_STATUS_CHECK_WAIT     = 1, /* Queued to check files */
# TR_STATUS_CHECK          = 2, /* Checking files */
# TR_STATUS_DOWNLOAD_WAIT  = 3, /* Queued to download */
# TR_STATUS_DOWNLOAD       = 4, /* Downloading */
# TR_STATUS_SEED_WAIT      = 5, /* Queued to seed */
# TR_STATUS_SEED           = 6  /* Seeding */

class Transmission():

	session_id = ''

	def __init__(self, database):
		self.database = database

	def status_code_409(self, data):
		self.session_id = data.split('X-Transmission-Session-Id: ')[1].split('</code></p>')[0]

	def add_torrent(self, download):
		for rs in self.database.execute("SELECT * FROM config WHERE config LIKE 'client_transmission_%'", None):
			if(rs[1] == 'client_transmission_host'):
				client_transmission_host = str(rs[3])
			if(rs[1] == 'client_transmission_rpc_url'):
				client_transmission_rpc_url = str(rs[3])
			if(rs[1] == 'client_transmission_username'):
				client_transmission_username = str(rs[3])
			if(rs[1] == 'client_transmission_password'):
				client_transmission_password = str(rs[3])

		data = {"method": "torrent-add", "arguments": {"filename": download}}
		headers = {'X-Transmission-Session-Id': self.session_id}
		r = requests.post(client_transmission_host + '/' + client_transmission_rpc_url + '/rpc/', auth=HTTPBasicAuth(client_transmission_username, client_transmission_password), headers=headers, json=data)

		# Wrong authentication
		if r.status_code == 401:
			logging.error('Transmission: Wrong authentication')
			return

		# Bad X-Transmission-Session-Id
		if r.status_code == 409:
			self.status_code_409(r.text)
			hashString = self.add_torrent(download)

		#logging.info('r.text ' + r.text)
		# OK!
		if r.status_code == 200:
			try:
				hashString = r.json()['arguments']['torrent-added']['hashString']
			except KeyError, e:
				try:
					hashString = r.json()['arguments']['torrent-duplicate']['hashString']
				except KeyError, e:
					logging.error('torrent-added torrent-duplicate failed :(')
					return None
		return hashString

	def check_completed(self):
		hashStrings = []
		
		for rs in self.database.execute("SELECT * FROM config WHERE config LIKE 'client_transmission_%'", None):
			if(rs[1] == 'client_transmission_host'):
				client_transmission_host = str(rs[3])
			if(rs[1] == 'client_transmission_rpc_url'):
				client_transmission_rpc_url = str(rs[3])
			if(rs[1] == 'client_transmission_username'):
				client_transmission_username = str(rs[3])
			if(rs[1] == 'client_transmission_password'):
				client_transmission_password = str(rs[3])

		data = {"method": "torrent-get", "arguments": {"fields": [ 'id', 'percentDone', 'hashString', 'downloadDir', 'name' ]}}
		headers = {'X-Transmission-Session-Id': self.session_id}
		r = requests.post(client_transmission_host + '/' + client_transmission_rpc_url + '/rpc/', auth=HTTPBasicAuth(client_transmission_username, client_transmission_password), headers=headers, json=data)

		# Wrong authentication
		if r.status_code == 401:
			logging.error('Transmission: Wrong authentication')
			return

		# Bad X-Transmission-Session-Id
		if r.status_code == 409:
			self.status_code_409(r.text)
			headers = {'X-Transmission-Session-Id': self.session_id}
			r = requests.post(client_transmission_host + '/' + client_transmission_rpc_url + '/rpc/', auth=HTTPBasicAuth(client_transmission_username, client_transmission_password), headers=headers, json=data)

		# OK!
		if r.status_code == 200:
			torrents = r.json()['arguments']['torrents']
			for torrent in torrents:
				hashString = torrent['hashString']
				hashStrings.append(hashString)
				percentDone = torrent['percentDone']
				path = torrent['downloadDir'] + '/' + torrent['name']

				if percentDone == 1:
					self.handle_completed(hashString, path)

		# Remove db torrents if they are not in transmisson
		for hash in self.database.execute('SELECT hashString FROM downloading WHERE 1', []):
			if hash[0] not in hashStrings:
				self.database.execute("DELETE FROM downloading WHERE `hashString`=?", [hash[0]])

	def handle_completed(self, hashString, path):
		source = None
		destination = None

		for rs in self.database.execute("SELECT * FROM downloading WHERE hashString=?", [hashString]):

			tvshow_id = rs[1]
			epsiode_id = rs[2]
			movie_id = rs[3]

			# tvshow
			if tvshow_id != None and epsiode_id != None:

				# File
				if os.path.isfile(path):
					logging.info('File')
					ext = os.path.splitext(path)[1][1:]
					if ext in extensions_videos:

						for tvshow in self.database.execute('SELECT path FROM tvshow WHERE tvshow_id=?', [tvshow_id]):
							destination = tvshow[0]
						for season in self.database.execute('SELECT SeasonNumber FROM episode WHERE episode_id=?', [epsiode_id]):
							destination += '/Season %02d/' % int(season[0])
						destination += os.path.basename(path)
						if os.path.isfile(destination):
							os.remove(destination)

						source = path

						self.database.execute('UPDATE episode SET path=? WHERE episode_id=?', [destination, epsiode_id])

						if "E01E02" in destination or "E01 E02" in destination or "E01-E02" in destination:
							for rs_2 in self.database.execute('SELECT episode_id FROM episode WHERE seriesid=? AND EpisodeNumber=?', [tvshow_id, 2]):
								logging.info(rs_2[0])
								self.database.execute('UPDATE episode SET path=? WHERE episode_id=?', [destination, rs_2[0]])

				# Directory
				elif os.path.isdir(path):
					logging.info('Directory')
					for filename in os.listdir(path):
						ext = os.path.splitext(filename)[1][1:]
						if ext in extensions_videos:

							for tvshow in self.database.execute('SELECT path FROM tvshow WHERE tvshow_id=?', [tvshow_id]):
								destination = tvshow[0]
							for season in self.database.execute('SELECT SeasonNumber FROM episode WHERE episode_id=?', [epsiode_id]):
								destination += '/Season %02d/' % int(season[0])
							destination += filename
							if os.path.isfile(destination):
								os.remove(destination)

							source = path + '/' + filename

							self.database.execute('UPDATE episode SET path=? WHERE episode_id=?', [destination, epsiode_id])

							if "E01E02" in destination or "E01 E02" in destination or "E01-E02" in destination:
								for rs_2 in self.database.execute('SELECT episode_id FROM episode WHERE seriesid=? AND EpisodeNumber=?', [tvshow_id, 2]):
									logging.info(rs_2[0])
									self.database.execute('UPDATE episode SET path=? WHERE episode_id=?', [destination, rs_2[0]])

			# movie
			if movie_id != None:
				pass

			if source == None or destination == None:
				continue
			
			try:
				logging.info('Moving completed torrent: %s to %s ' % (source, destination))
				shutil.move(source, destination)
			except OSError, UnboundLocalError:
				logging.info('Source could not be found: %s' % source)
			self.remove_torrent(hashString)

	def remove_torrent(self, hashString):
		for rs in self.database.execute("SELECT * FROM config WHERE config LIKE 'client_transmission_%'", None):
			if(rs[1] == 'client_transmission_host'):
				client_transmission_host = str(rs[3])
			if(rs[1] == 'client_transmission_rpc_url'):
				client_transmission_rpc_url = str(rs[3])
			if(rs[1] == 'client_transmission_username'):
				client_transmission_username = str(rs[3])
			if(rs[1] == 'client_transmission_password'):
				client_transmission_password = str(rs[3])

		data = {"method": "torrent-get", "arguments": {"fields": [ 'id', 'percentDone', 'hashString', 'downloadDir', 'name' ]}}
		headers = {'X-Transmission-Session-Id': self.session_id}
		r = requests.post(client_transmission_host + '/' + client_transmission_rpc_url + '/rpc/', auth=HTTPBasicAuth(client_transmission_username, client_transmission_password), headers=headers, json=data)

		# Wrong authentication
		if r.status_code == 401:
			logging.error('Transmission: Wrong authentication')
			return

		# Bad X-Transmission-Session-Id
		if r.status_code == 409:
			self.status_code_409(r.text)
			headers = {'X-Transmission-Session-Id': self.session_id}
			r = requests.post(client_transmission_host + '/' + client_transmission_rpc_url + '/rpc/', auth=HTTPBasicAuth(client_transmission_username, client_transmission_password), headers=headers, json=data)

		# OK!
		if r.status_code == 200:

			torrents = r.json()['arguments']['torrents']

			for torrent in torrents:

				if hashString == torrent['hashString']:

					id = torrent['id']

					data = {"method": "torrent-remove", "arguments": {"ids": [ id ], "delete-local-data": 'true'}}
					headers = {'X-Transmission-Session-Id': self.session_id}
					r = requests.post(client_transmission_host + '/' + client_transmission_rpc_url + '/rpc/', auth=HTTPBasicAuth(client_transmission_username, client_transmission_password), headers=headers, json=data)	

					# Wrong authentication
					if r.status_code == 401:
						logging.error('Transmission: Wrong authentication')
						return

					# Bad X-Transmission-Session-Id
					if r.status_code == 409:
						self.status_code_409(r.text)
						headers = {'X-Transmission-Session-Id': self.session_id}
						r = requests.post(client_transmission_host + '/' + client_transmission_rpc_url + '/rpc/', auth=HTTPBasicAuth(client_transmission_username, client_transmission_password), headers=headers, json=data)

					# OK!
					if r.status_code == 200:
						self.database.execute('DELETE FROM downloading WHERE hashString=?', [hashString])