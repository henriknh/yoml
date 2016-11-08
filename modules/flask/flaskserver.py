from functools import wraps
from packages.flask.flask import Flask, session, render_template, current_app, request, redirect, url_for, flash, make_response, send_from_directory
import logging, thread, os, json, urllib, urllib2, socket
from datetime import datetime

app = Flask(__name__, template_folder="../../www", static_folder ="../../www/static")

def FlaskServer(library_temp, config_temp, ffmpeg_temp, port):

	logging.info("Flask started on port %s" % (str(port)))

	global library
	library = library_temp
	global config
	config = config_temp
	global ffmpeg
	ffmpeg = ffmpeg_temp

	app.secret_key = '5DvMqpaV6u63AvC4HkDsB73wxwanHRlf41cyDvo2C3Pe2jPUBqON4xe0eYjvWIJz4r723H7C2HTRsMlRSMpfcuv7PfEDFxEJBhmb'

	app.config['USERNAME'] = 'user'
	app.config['PASSWORD'] = 'pass'

	app.run(debug=False, host='0.0.0.0', port=int(port), threaded=True)

	session.modified = True

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if session.get('logged_in') is not True:
			return redirect(url_for('login', next=request.url))
		return f(*args, **kwargs)
	return decorated_function

def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ('http', 'https') and \
		ref_url.netloc == test_url.netloc

def get_redirect_target():
	for target in request.values.get('next'), request.referrer:
		if not target:
			continue
		if is_safe_url(target):
			return target

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

@app.route('/')
@login_required
def index():
	data_progress = library.get_progressed_media()
	data_recommended = None
	data_new = None
	return render_template('dash.html', progress=data_progress, recommended=data_recommended, new=data_new, fanart=library.get_random_tvshow_fanart(), config=config.get_config())

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('index'))
	return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('index'))

@app.route('/tvshows')
@login_required
def tvshows():
	return render_template('tvshows.html', tvshows=library.get_tvshows(), fanart=library.get_random_tvshow_fanart(), config=config.get_config())
		

@app.route('/tvshows/<int:tvshow>')
@login_required
def tvshow(tvshow):
	data_tvshow = library.get_tvshow(tvshow)
	return render_template('tvshow.html', tvshow=data_tvshow[0], episodes=data_tvshow[1], config=config.get_config(), servertime=datetime.now())


@app.route('/tvshows/<int:tvshow>/<int:episode>')
@login_required		
def episode(tvshow, episode):
	data_episode = library.get_data_episode(tvshow, episode)
	return render_template('episode.html', tvshow=data_episode[0], episode=data_episode[1], config=config.get_config())


@app.route('/tvshows/<int:tvshow>/<int:episode>/player')
@login_required
def episodeplayer(tvshow, episode):
	data_player = library.get_data_episode_player(tvshow, episode)
	return render_template('episodeplayer.html', tvshow=data_player[0], episode=data_player[1], videoinfo=data_player[2], config=config.get_config())

@app.route('/static/temp/<path:manifest>', methods=['GET', 'POST'])
@login_required
def manifest_download(manifest):
	
	manifest_dir = os.path.abspath(os.path.join(app.root_path, '..\\..\\www\\static\\temp'))
	file = manifest_dir+'\\'+manifest
	filename, file_extension = os.path.splitext(file)

	response = make_response(send_from_directory(manifest_dir, manifest, as_attachment=True))
	
	if file_extension == '.m3u8':
		response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
		response.headers['Pragma'] = 'no-cache'
		response.headers['Expires'] = '0'

	return response

@app.after_request
def add_header(response):
	"""
	Add headers to both force latest IE rendering engine or Chrome Frame,
	and also to cache the rendered page for 10 minutes.
	"""
	#response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	#response.headers["Pragma"] = "no-cache"
	#response.headers["Expires"] = "0"
	return response

@app.route('/movies')
@login_required
def movies():
	return render_template('movies.html', config=config.get_config())

@app.route('/pictures')
@login_required
def pictures():
	return render_template('pictures.html', config=config.get_config())

@app.route('/music')
@login_required
def music():
	return render_template('music.html', config=config.get_config())

@app.route('/settings')
@app.route('/settings/<settings>')
@login_required
def settings(settings=None):
	data = None
	if settings == None or settings == 'general':
		data = 'general'
	elif settings == 'display':
		data = 'display'
	elif settings == 'manage':
		data = library.get_manage_media()
	elif settings == 'client':
		data = 'download client'
	elif settings == 'torrent':
		data = 'torrent'
	elif settings == 'statistics':
		data = library.get_statistics()
	elif settings == 'about':
		data = 'about'
	else:
		return render_template('static/util/page_not_found.html'), 404

	return render_template('settings.html', data=data, config=config.get_config())

@app.errorhandler(404)
@login_required
def page_not_found(error):
	return render_template('static/util/page_not_found.html'), 404


@app.route('/stop/<m3u8>', methods=['GET', 'POST'])
@login_required		
def stop(m3u8):
	thread.start_new_thread(ffmpeg.stop_transcoding,(str(m3u8),))
	return 'OK'


@app.route('/retranscode/<m3u8>/<time>', methods=['GET', 'POST'])
@login_required		
def retranscode(m3u8, time):
	logging.info("retranscoding %s " + str(m3u8))
	logging.info("retranscoding %s " + str(time))
	path = ffmpeg.stop_transcoding(str(m3u8))
	logging.info("retranscoding %s " + str(path))
	if path != None:
		m3u8 = ffmpeg.run_ffmpeg(path, time)
	return m3u8

@app.route('/filetree/<path:path>', methods=['GET', 'POST'])
@login_required		
def filetree(path):
	path = urllib2.unquote(path).replace("//", "/")
	if path == 'root':
		if os.name == 'nt':
			drives = [chr(x) + ":/" for x in range(65,90) if os.path.exists(chr(x) + ":")]
			
			folders = [['/']]
			for drive in drives:
				folders.append([drive, drive])
			return json.dumps(folders)
		else:
			path = json.dumps([['/', '/']])

	try:
		parent = path.rsplit('/',1)[0]
		if parent.count('/') == 0:
			parent = parent + "/"
		if parent == path:
			parent = 'root'
		folders = [[path], [parent, '..']]
		files = os.listdir(path)
		for file in files:
			if os.path.isdir(path + '/' + file):
				folders.append([path + '/' + file, file])
		
		return json.dumps(folders)
	except IOError:
		return None

@app.route('/new_library', methods=['POST'])
@login_required		
def new_library():
	thread.start_new_thread(library.new_library,(request.form['library_type'], request.form['path'],))
	return redirect(redirect_url())

@app.route('/remove_library/<int:id>', methods=['POST'])
@login_required		
def remove_library(id):
	thread.start_new_thread(library.remove_library,(id,))
	return redirect(redirect_url())

@app.route('/searchtvshow/<query>', methods=['GET', 'POST'])
@login_required		
def searchtvshow(query):
	query = urllib.quote(query.encode('utf-8'))
	file = urllib2.urlopen('http://thetvdb.com/api/GetSeries.php?seriesname=' + query)
	data = file.read()
	file.close()
	return data

@app.route('/setconfig/<int:config_id>/<value>', methods=['GET', 'POST'])
@login_required		
def setconfig(config_id, value):
	config.set_config(config_id, value)
	return 'OK'

@app.route('/getlibrariesformodal', methods=['GET', 'POST'])
@login_required		
def getlibrariesformodal():
	return library.get_libraries_xml()

@app.route('/new_media/<type>/<media>/<int:library_id>', methods=['POST'])
@login_required		
def new_media(type, media, library_id):
	library.new_media(type, media, library_id)
	return 'OK'

@app.route('/refresh_media/<type>/<int:id>', methods=['POST'])
@login_required		
def refresh_tvshow(type, id):
	thread.start_new_thread(library.refresh_media,(type, id,))
	return 'OK'

@app.route('/toggle_media_watched/<type>/<int:id>/<int:watched>', methods=['POST'])
@login_required		
def toggle_tvshow_watched(type, id, watched):
	thread.start_new_thread(library.toggle_media_watched,(type, id, watched,))
	return 'OK'

@app.route('/remove_media/<type>/<int:id>', methods=['POST'])
@login_required		
def remove_tvshow(type, id):
	thread.start_new_thread(library.remove_media,(type, id,))
	return 'OK'

@app.route('/test_port/<int:port>', methods=['GET', 'POST'])
@login_required		
def test_port(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#sock.bind((socket.gethostname(), port))
	#sock.listen(5)
	result = sock.connect_ex(('127.0.0.1',port))
	if result == 0:
		return '1'
	else:

		return '0'

@app.route('/search/<query>', methods=['GET', 'POST'])
@login_required		
def search(query):
	return library.search(query)

@app.route('/update_config', methods=['POST'])
def update_config():
	f = request.form
	keys = f.keys()
	values = f.values()

	logging.debug('keys: ' + str(keys))
	logging.debug('values: ' + str(values))

	for config_id in keys:
		value = f.getlist(config_id)[0]
		config.set_config(config_id, value)

	return redirect(request.referrer)


@app.template_filter('datetime')
def filterdatetime(value):
    return datetime.strptime(value, '%Y-%m-%d')