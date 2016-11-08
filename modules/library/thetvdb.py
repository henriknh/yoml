# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
import xml.dom.minidom
import urllib
import os
import logging
from modules.util.util import *
import datetime
import urllib2

class TheTVDB():

	workdir = os.getcwd()

	def get_tvshow_seriesid(self, tvshow):

		file = urllib.urlopen('http://thetvdb.com/api/GetSeries.php?seriesname=' + urllib.quote(unicode(tvshow).encode('utf8'), ':/'))
		tvshows = file.read()
		file.close()

		DOMTree = xml.dom.minidom.parseString(tvshows)
		collection = DOMTree.documentElement

		tvshow = collection.getElementsByTagName("Series")
		seriesid = tvshow[0].getElementsByTagName('seriesid')[0]

		return seriesid.childNodes[0].data

	def download_tvshow_data(self, seriesid, destination):
		if not os.path.exists(destination):
			os.makedirs(destination)

		#file = open(destination + '/data.xml', 'w+')
		#file.close()

		urllib.urlretrieve ('http://thetvdb.com/api/2B568426EB9C1667/series/' + seriesid + '/all/en.xml', destination + '/data.xml')
		#urllib.urlretrieve ('http://thetvdb.com/api/2B568426EB9C1667/series/' + seriesid + '/banners.xml', destination + '/banner.xml')
		#urllib.urlretrieve ('http://thetvdb.com/api/2B568426EB9C1667/series/' + seriesid + '/actors.xml', destination + '/actors.xml')

	def get_tvshow_name(self, seriesid):
		file = urllib2.urlopen('http://thetvdb.com/api/2B568426EB9C1667/series/' + str(seriesid) + '/all/en.xml')
		data = file.read()
		file.close()
		
		return data.split('<SeriesName>')[1].split('</SeriesName>')[0]

	def get_tvshow_data(self, library_id, seriesid, destination, path, database):
		file = open(destination + '/data.xml', 'r')
		data = file.read()

		DOMTree = xml.dom.minidom.parseString(data)
		collection = DOMTree.documentElement

		sql = 'INSERT INTO `tvshow` VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

		data = []

		tvshow = collection.getElementsByTagName("Series")


		temp = tvshow[0].getElementsByTagName('id')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)

		data.append(library_id)
			
		temp = tvshow[0].getElementsByTagName('Actors')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('ContentRating')[0].childNodes

		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('FirstAired')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('Genre')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('IMDB_ID')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('Network')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('Overview')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('Rating')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('Runtime')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('SeriesName')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('Status')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('banner')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('fanart')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			download_fanart_image('http://thetvdb.com/banners/' + temp[0].data, self.workdir + '/www/static/banners/' + temp[0].data)
			
		temp = tvshow[0].getElementsByTagName('poster')[0].childNodes
		if len(temp) == 0:
			data.append('')
		else:
			data.append(temp[0].data)
			download_posters_image('http://thetvdb.com/banners/' + temp[0].data, self.workdir + '/www/static/banners/' + temp[0].data)

		data.append(path)

		file.close()

		# Insert tv show data to DB
		tvshow_exists = database.execute('SELECT Count(*) FROM `tvshow` WHERE `tvshow_id`=?', [seriesid])
		exists = 0
		for e in tvshow_exists:
			if e[0] == 1:
				exists = 1
		if exists == 1:
			database.execute('UPDATE `tvshow` SET `tvshow_id`=?,`library_id`=?,`Actors`=?,`ContentRating`=?,`FirstAired`=?,`Genre`=?,`IMDB_ID`=?,`Network`=?,`Overview`=?,`Rating`=?,`Runtime`=?,`SeriesName`=?,`Status`=?,`banner`=?,`fanart`=?,`poster`=?,`path`=? WHERE `tvshow_id`=?', data + [seriesid])
		else:
			database.execute(sql, data)

	def get_episode_data(self, library_id, seriesid, destination, path, database):

		file = open(destination + '/data.xml', 'r')
		data = file.read()
		file.close()

		DOMTree = xml.dom.minidom.parseString(data)
		collection = DOMTree.documentElement

		sql = 'INSERT INTO `episode` VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

		data = []

		episodes = collection.getElementsByTagName("Episode")

		for episode in episodes:
			data = []

			episode_id = 0

			# Check if season number if higher than 0
			season_number = episode.getElementsByTagName('SeasonNumber')[0].childNodes[0].data
			if str(season_number) == '0':
				continue


			temp = episode.getElementsByTagName('id')[0].childNodes
			if len(temp) == 0:
				data.append('')
			else:
				episode_id = temp[0].data
				data.append(episode_id)

			data.append(library_id)

			temp = episode.getElementsByTagName('Director')[0].childNodes
			if len(temp) == 0:
				data.append('')
			else:
				data.append(temp[0].data)

			temp = episode.getElementsByTagName('EpisodeName')[0].childNodes
			if len(temp) == 0:
				data.append('')
			else:
				data.append(temp[0].data)

			temp = episode.getElementsByTagName('EpisodeNumber')[0].childNodes
			EpisodeNumber = 0
			if len(temp) == 0:
				data.append('')
			else:
				EpisodeNumber = temp[0].data
				data.append(temp[0].data)

			temp = episode.getElementsByTagName('FirstAired')[0].childNodes
			if len(temp) == 0:
				data.append('')
			else:
				data.append(temp[0].data)
				FirstAired = temp[0].data

			temp = episode.getElementsByTagName('Overview')[0].childNodes
			if len(temp) == 0:
				data.append('')
			else:
				data.append(temp[0].data)

			temp = episode.getElementsByTagName('Rating')[0].childNodes
			if len(temp) == 0:
				data.append('')
			else:
				data.append(temp[0].data)

			temp = episode.getElementsByTagName('SeasonNumber')[0].childNodes
			SeasonNumber = 0
			if len(temp) == 0:
				data.append('')
			else:
				SeasonNumber = temp[0].data
				data.append(temp[0].data)

			temp = episode.getElementsByTagName('Writer')[0].childNodes
			if len(temp) == 0:
				data.append('')
			else:
				data.append(temp[0].data)

			temp = episode.getElementsByTagName('absolute_number')[0].childNodes
			absolute_number = 0
			if len(temp) == 0:
				data.append('')
			else:
				absolute_number = temp[0].data
				data.append(temp[0].data)

			temp = episode.getElementsByTagName('filename')[0].childNodes
			if len(temp) == 0:
				data.append('')
			else:
				data.append(temp[0].data)
				episode_thumbnail = temp[0].data
				
			temp = episode.getElementsByTagName('seriesid')[0].childNodes
			if len(temp) == 0:
				data.append('')
			else:
				data.append(temp[0].data)
				seriesid = temp[0].data

			#path
			episode_path = self.search_for_episode(path, SeasonNumber, EpisodeNumber, absolute_number)
			if episode_path == None:
				data.append('')
			else:
				data.append(episode_path)

			# Download episode image and thumbnail
			if FirstAired != None:
				date1 = datetime.datetime.now().date()
				date2 = datetime.datetime.strptime(FirstAired, "%Y-%m-%d").date()

				if date1 > date2:
					download_episodes_image('http://thetvdb.com/banners/episodes/' + seriesid + '/' + episode_id + '.jpg', self.workdir + '/www/static/banners/episodes/' + seriesid + '/' + episode_id + '.jpg', episode_path)

			# Insert episode data to DB
			episode_exists = database.execute('SELECT Count(*) FROM `episode` WHERE `episode_id`=?', [episode_id])
			exists = 0
			for e in episode_exists:
				if e[0] == 1:
					exists = 1
			if exists == 1:
				database.execute('UPDATE `episode` SET `episode_id`=?,`library_id`=?,`Director`=?,`EpisodeName`=?,`EpisodeNumber`=?,`FirstAired`=?,`Overview`=?,`Rating`=?,`SeasonNumber`=?,`Writer`=?,`absolute_number`=?,`filename`=?,`seriesid`=?,`path`=? WHERE `episode_id`=?', data + [episode_id])
			else:
				database.execute(sql, data)

			# Insert connection between tvshow and episode to DB
			#episode_exists = database.execute('SELECT Count(*) FROM `episode` WHERE `episode_id`=?', [episode_id])
			#exists = 0
			#for e in episode_exists:
			#	if e[0] == 1:
			#		exists = 1
			#if exists == 1:
			#	database.execute('UPDATE `tvshow_has_episode` SET `tvshow_tvshow_id`=?,`episode_episode_id`=? WHERE `episode_episode_id`=?', [seriesid , episode_id] + [episode_id])
			#else:
			#	database.execute('INSERT INTO `tvshow_has_episode` VALUES (?,?)', [seriesid , episode_id])

	def search_for_episode(self, path, season, episode, absolute_number):
		season_path = path + '/Season %02d/' % int(season)

		if not os.path.exists(season_path):
			os.makedirs(season_path)

		file_list = os.listdir(season_path)

		for file in file_list:

			logging.info("Search for local episode: (Season %s), (Episode %s), (Absolute Number %s) %s " % (season, episode, absolute_number, file))

			'''
				Dual episodes
			'''

			# S__E__E00
			if ('S%02dE%02dE%02d' % (int(season), int(episode), int(episode)+1)).lower() in file.lower():
				return season_path + file

			# S__E00E__
			if ('S%02dE%02dE%02d' % (int(season), int(episode)-1, int(episode))).lower() in file.lower():
				return season_path + file

			# S__E__ E00
			if ('S%02dE%02d E%02d' % (int(season), int(episode), int(episode)+1)).lower() in file.lower():
				return season_path + file

			# S__E00 E__
			if ('S%02dE%02d E%02d' % (int(season), int(episode)-1, int(episode))).lower() in file.lower():
				return season_path + file

			# S__E__-E00
			if ('S%02dE%02d-E%02d' % (int(season), int(episode), int(episode)+1)).lower() in file.lower():
				return season_path + file

			# S__E00-E__
			if ('S%02dE%02d-E%02d' % (int(season), int(episode)-1, int(episode))).lower() in file.lower():
				return season_path + file

			'''
				Single episodes
			'''

			# S__E__
			if ('S' + '%02d' % int(season) + 'E' + '%02d' % int(episode)).lower() in file.lower():
				return season_path + file

			# Part _
			if ('Part ' + '%01d' % int(episode)).lower() in file.lower():
				return season_path + file

			# Part __
			if ('Part ' + '%02d' % int(episode)).lower() in file.lower():
				return season_path + file

			# Ep xx
			if ('Ep %02d' % int(episode)).lower() in file.lower():
				return season_path + file

			# Epxx
			if ('Ep%02d' % int(episode)).lower() in file.lower():
				return season_path + file

			# xx (absolute_number)
			if (' %02d ' % int(absolute_number)).lower() in file.lower():
				return season_path + file

			# xx (episode)
			if (' %02d ' % int(episode)).lower() in file.lower():
				return season_path + file