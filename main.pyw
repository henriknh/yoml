# -*- coding: utf-8 -*-

# https://www.crazydomains.co.uk/domain-names/search/?domain=home.tv&tab=popular_tab
# http://data.iana.org/TLD/tlds-alpha-by-domain.txt
# gallery
# theatre
# tube
# play
# media
# tv

# yoml.tv


# Packages
import time
import logging, os
from packages.appdirs.appdirs import *

# Modules
from modules.subtitle.subtitle import *
from modules.config.config import *
from modules.database.database import *
from modules.ffmpeg.ffmpeg import *
from modules.flask.flaskserver import *
from modules.library.library import *
from modules.torrent.torrent import *
from modules.torrent.torrentapi import *
from modules.tray.tray import *

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

version = 0.1
title = "MediaLibrary"
author = ""

# Create files if they doesnt exists
dataDir = user_data_dir(title, '', roaming=True)

# Database
database = Database(dataDir)

# Config
config = Config(database)

# Subtitle
subtitleUsername = 'ziggestark'
subtitlepassword = 'swormaster1'
subtitle = Subtitle(subtitleUsername, subtitlepassword)
#subtitle = None

# FFMPEG
ffmpeg = ffmpeg(config, subtitle)
ffmpeg.clean_ffmpeg()

# Torrent
torrent = Torrent(database)
torrentapi = TorrentAPI(torrent, database)

# Library
library = Library(dataDir, database, ffmpeg, torrent, torrentapi)
#reqhandler = RequestHandler(library, database)

# Flask
for rs in database.execute("SELECT value FROM config WHERE config='general_flask_port'", None):
	port = rs[0]
if port != None:
	thread.start_new_thread(FlaskServer,(library, config, ffmpeg, port,))




# System tray
app = App(False)
app.set_icon('www/static/icons/icon.png', title)
app.set_classes(database, library, ffmpeg)
app.MainLoop()
thread.start_new_thread(app.MainLoop,())