from PIL import Image
from packages.resizeimage.resizeimage import *
import urllib, urllib2
import os
import logging
from urllib2 import urlopen, URLError, HTTPError

extensions_videos = ['mkv', 'mp4', 'avi']
extensions_pictures = ['jpg', 'jpeg', 'png']
extensions_music = ['mp3']

def download_episodes_image(source, destination, episode_path):

	if os.path.isfile(destination) and os.stat(destination).st_size != 0:
		return

	directory_exists(os.path.dirname(destination))

	if source != '':
		rs = download(source, destination)	
	
	if episode_path != '' and rs == False:
		print 'Create episode thumb from file'

		rs = False


	if rs == True:
		with open(destination, 'r+b') as f:
			with Image.open(f) as image:
				cover = resize_thumbnail(image, [277, 156])
				cover.save("{0}{2}.{1}".format(*destination.rsplit('.', 1) + ['-thumb']), image.format)

	return True



def download_fanart_image(source, destination):

	if os.path.isfile(destination) and os.stat(destination).st_size != 0:
		return

	directory_exists(os.path.dirname(destination))

	if source != '':
		rs = download(source, destination)
		return rs
	return False


def download_posters_image(source, destination):

	if os.path.isfile(destination) and os.stat(destination).st_size != 0:
		return
	
	directory_exists(os.path.dirname(destination))

	if source != '':
		rs = download(source, destination)
		if rs == True:	
			with open(destination, 'r+b') as f:
				with Image.open(f) as image:
					cover = resize_thumbnail(image, [197, 290])
					cover.save("{0}{2}.{1}".format(*destination.rsplit('.', 1) + ['-thumb']), image.format)

		return rs
	return False

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