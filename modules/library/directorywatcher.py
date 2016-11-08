import sys
import time
import logging
#from packages.watchdog.observers import Observer
#from watchevents import *


class DirectoryWatcher():

	logging.basicConfig(level=logging.INFO,
							format='%(asctime)s - %(message)s',
							datefmt='%Y-%m-%d %H:%M:%S')

	#tvshows_event_handler = TVShowsEventHandler()
	#movies_event_handler = MoviesEventHandler()
	#pictures_event_handler = PicturesEventHandler()
	#music_event_handler = MusicEventHandler()
	#observer = Observer()

	def add_watch(self, library):
		'''
		if library.type == 'tvshows':
			for path in library.paths:
				#self.observer.schedule(self.tvshows_event_handler, path, recursive=True)
		if library.type == 'movies':
			for path in library.paths:
				#self.observer.schedule(self.movies_event_handler, path, recursive=True)
		if library.type == 'pictures':
			for path in library.paths:
				self.observer.schedule(self.pictures_event_handler, path, recursive=True)
		if library.type == 'music':
			for path in library.paths:
				self.observer.schedule(self.music_event_handler, path, recursive=True)
		'''
		pass

	def start(self):
		#self.observer.start()
		##try:
		##	while True:
		##		time.sleep(1)
		##except KeyboardInterrupt:
		##	observer.stop()
		#self.observer.join()
		pass