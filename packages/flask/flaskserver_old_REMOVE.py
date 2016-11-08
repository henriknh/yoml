from functools import wraps
from flask import Flask, session, render_template, current_app, request, redirect, url_for, flash
import logging
import thread

app = Flask(__name__, template_folder="../../www", static_folder ="../../www/static")

def FlaskServer(library_temp, ffmpeg_temp, port):

	logging.info("Flask started on port %s" % (str(port)))

	global library
	library = library_temp
	global ffmpeg
	ffmpeg = ffmpeg_temp

	app.secret_key = '5DvMqpaV6u63AvC4HkDsB73wxwanHRlf41cyDvo2C3Pe2jPUBqON4xe0eYjvWIJz4r723H7C2HTRsMlRSMpfcuv7PfEDFxEJBhmb'

	app.config['USERNAME'] = 'user'
	app.config['PASSWORD'] = 'pass'

	app.run(debug=True, host='0.0.0.0', port=int(24800), threaded=True)

	session.modified = True

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if session.get('logged_in') is not True:
			return redirect(url_for('login', next=request.url))
		return f(*args, **kwargs)
	return decorated_function

@app.route('/')
@login_required
def index():
	data_progress = library.get_progressed_media()
	data_recommended = ""
	data_new = ""
	return render_template('dash.html', progress=data_progress, recommended=data_recommended, new=data_new)

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
	return render_template('tvshows.html', tvshows=library.get_tvshows())
		

@app.route('/tvshows/<int:tvshow>')
@login_required
def tvshow(tvshow):
	data_tvshow = library.get_tvshow(tvshow)
	return render_template('tvshow.html', tvshow=data_tvshow[0], episodes=data_tvshow[1])


@app.route('/tvshows/<int:tvshow>/<int:episode>')
@login_required		
def episode(tvshow, episode):
	data_episode = library.get_data_episode(tvshow, episode)
	return render_template('episode.html', tvshow=data_episode[0], episode=data_episode[1])


@app.route('/tvshows/<int:tvshow>/<int:episode>/player')
@login_required		
def episodeplayer(tvshow, episode):
	data_player = library.get_data_episode_player(tvshow, episode)
	return render_template('episodeplayer.html', tvshow=data_player[0], episode=data_player[1], videoinfo=data_player[2])

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
	m3u8 = ffmpeg.run_ffmpeg(path, time)
	return m3u8