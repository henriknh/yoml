import logging
import thread
import threading
from random import randint
from transmission import *



class Torrent():

	def __init__(self, database):
		self.database = database

		self.transmission = Transmission(database)

		logging.getLogger("requests").setLevel(logging.WARNING)

		thread.start_new_thread(self.check_completed_timer,())

	
	def add_torrent(self, download):

		logging.info('Add torrent: ' + download)

		for rs in self.database.execute("SELECT value FROM config WHERE config='client_current_client'", None):
			client_current_client = rs[0]

		hashString = None

		if client_current_client == 'Transmission':
			hashString = self.transmission.add_torrent(download)
			
		return hashString

	def check_completed_timer(self):

		for rs in self.database.execute("SELECT value FROM config WHERE config='torrent_check_completed_interval'", None):
			torrent_check_completed_interval = rs[0]
		
		self.check_completed()

		threading.Timer(float(torrent_check_completed_interval)*60, self.check_completed_timer).start()

	def check_completed(self):

		logging.info('Check completed torrents')

		for rs in self.database.execute("SELECT value FROM config WHERE config='client_current_client'", None):
			client_current_client = rs[0]

		if client_current_client == 'Transmission':
			hashString = self.transmission.check_completed()

		return

	def remove_torrent(self, hashString):

		logging.info('Removing torrent: ' + hashString)

		for rs in self.database.execute("SELECT value FROM config WHERE config='client_current_client'", None):
			client_current_client = rs[0]

		if client_current_client == 'Transmission':
			hashString = self.transmission.remove_torrent(hashString)

		return