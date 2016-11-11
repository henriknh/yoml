from packages.resizeimage.resizeimage import *
from PIL import Image
import urllib, urllib2
import os
import logging
from urllib2 import urlopen, URLError, HTTPError

extensions_videos = ['mkv', 'mp4', 'avi']
extensions_pictures = ['jpg', 'jpeg', 'png']
extensions_music = ['mp3']

def download_episodes_image(source, destination, episode_path):

	directory_exists(os.path.dirname(destination))

	if (not os.path.isfile(destination) or os.stat(destination).st_size == 0) and source != '':
		rs = download(source, destination)
		if rs == False and episode_path != '':
			logging.info("Create episode thumbnail from file (util, download_episodes_image)")
		elif rs == False and episode_path == '':
			return False
	
	make_thumbnail(destination)

	return True

def download_fanart_image(source, destination):

	directory_exists(os.path.dirname(destination))

	if (not os.path.isfile(destination) or os.stat(destination).st_size == 0) and source != '':
		rs = download(source, destination)
		if rs == False:
			return False

	return True

def download_posters_image(source, destination):

	directory_exists(os.path.dirname(destination))

	if (not os.path.isfile(destination) or os.stat(destination).st_size == 0) and source != '':
		rs = download(source, destination)
		if rs == False:
			return False
	
	make_thumbnail(destination)

	return True

def make_thumbnail(source):
	with open(source, 'r+b') as f:
		with Image.open(f) as image:
			cover = resize_thumbnail(image, [197, 290])
			cover.save("{0}{2}.{1}".format(*source.rsplit('.', 1) + ['-thumb']), image.format)

def directory_exists(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)



def download(source, destination):
	# Open the url
	try:
		f = urlopen(source)
		
		# Open our local file for writing
		with open(destination, "wb") as local_file:
			local_file.write(f.read())

	#handle errors
	except HTTPError, e:
		return False
	except URLError, e:
		return False
	return True