var vid;
var timeoutHideElements;
var timeoffset = 0;

function onLoad_player() {
		vid = document.getElementById("player");
		vid.addEventListener("timeupdate", updateProgress, false);

		vid.width = window.innerWidth;
		vid.height = window.innerHeight;

		vid.style.visibility = 'hidden';
		resize(); // Bottom bar
		setVolume();

		autoHideElements();
		document.onmousemove=function(){
				$('#bottomBar').show();
				//$('#playPauseMiddle').show();
				$('#topBar').show();
				clearTimeout(timeoutHideElements);
				autoHideElements();
		};
}

window.onresize = function(event) {
	resize();
};

function resize() {
	var progress = document.getElementById("progress");
	progress.style.width = window.innerWidth - 3 * 80 - 2 * 90 - 170 + "px";
	document.getElementById("content").style.minHeight = (window.innerHeight - 80) + 'px';
}

function autoHideElements() {
		timeoutHideElements =setTimeout(function() {
				$('#bottomBar').fadeOut('slow');
				//$('#playPauseMiddle').fadeOut('slow');
				$('#topBar').fadeOut('slow');
		}, 3000);
}

document.onkeydown = function(e) {
		e = e || window.event;
		var charCode = (typeof e.which == "number") ? e.which : e.keyCode;
		if (charCode == 32) { // Space
				togglePlayPause();
		}
		if (charCode == 37) { // Left arrow
		}
		if (charCode == 38) { // Up arrow
				var volume = document.getElementById("volume");
				volume.value = Number(volume.value) + 0.1;
				setVolume();
		}
		if (charCode == 39) { // Right arrow
		}
		if (charCode == 40) { // Down arrow
				var volume = document.getElementById("volume");
				volume.value = Number(volume.value) - 0.1;
				setVolume();
		}
		if (charCode == 77) { // M (Mute)
				toggleMute();
		}
};

function togglePlayPause() {
	 var playPause = document.getElementById("playPause");
	 if (vid.paused || vid.ended) {
			playPause.src = "/static/icons/pause.png";
			vid.style.visibility = 'visible';
			document.getElementById("playPauseMiddle").style.display = 'none';
			vid.play();
	 }
	 else {
			playPause.src = "/static/icons/play.png";
			vid.style.visibility = 'hidden';
			document.getElementById("playPauseMiddle").style.display = 'block';
			vid.pause();
	 }
}

var progressActive = false;
$(document).on('input change', '#progress', function() {
	console.log("input");
	progressActive = true;
	updateTime();
});
$(document).on('change', '#progress', function() {
	console.log("change");
	progressActive = false;
});
function updateProgress() {
	var progress = document.getElementById("progress");
	if(!progressActive){
		progress.value = (vid.currentTime+timeoffset)/videoDuration;
	}
	updateTime();
}

function updateTime() {
	var progress = document.getElementById("progress");
	var currentTime = document.getElementById("currentTime");
	var totalTime = document.getElementById("totalTime");
	timeVideo = progress.value * videoDuration;
	if((timeVideo/3600)%60 == 0) {
		currentTime.innerHTML = leftPad(Math.floor((timeVideo/60)%60), 2) + ':' + leftPad(Math.floor(timeVideo%60), 2);
	} else {
		currentTime.innerHTML = leftPad(Math.floor((timeVideo/3600)%60), 2) + ':' + leftPad(Math.floor((timeVideo/60)%60), 2) + ':' + leftPad(Math.floor(timeVideo%60), 2);
	}
	if((videoDuration/3600)%60 == 0) {
		totalTime.innerHTML = leftPad(Math.floor((videoDuration/60)%60), 2) + ':' + leftPad(Math.floor(videoDuration%60), 2);
	} else {
		totalTime.innerHTML = leftPad(Math.floor((videoDuration/3600)%60), 2) + ':' + leftPad(Math.floor((videoDuration/60)%60), 2) + ':' + leftPad(Math.floor(videoDuration%60), 2);
	}
}

function setProgress() {
	var progress = document.getElementById("progress");
	retranscode(videoDuration * progress.value);
}

function setVolume() {
	var volume = document.getElementById("volume");
	vid.volume = volume.value;
	vid.muted = false;
	mute.src = "/static/icons/volume-mute.png";
	if(volume.value < 0.33) {
		mute.src = "/static/icons/volume-low.png";
	} else if(volume.value > 0.66) {
		mute.src = "/static/icons/volume-high.png";
	} else {
		mute.src = "/static/icons/volume-medium.png";
	}
}

function toggleMute() {
		var mute = document.getElementById("mute");
		if(vid.muted == true) {
				setVolume();
				vid.muted = false;
		} else {
				mute.src = "/static/icons/volume-mute.png";
				vid.muted = true;
		}
}

function toggleFullscreen() {

	var fullscreen  = document.getElementById("fullscreen");

	if ((document.fullScreenElement && document.fullScreenElement !== null) ||    
		(!document.mozFullScreen && !document.webkitIsFullScreen)) {
	
		if (document.documentElement.requestFullScreen) {  
			document.documentElement.requestFullScreen();  
		} else if (document.documentElement.mozRequestFullScreen) {  
			document.documentElement.mozRequestFullScreen();  
		} else if (document.documentElement.webkitRequestFullScreen) {  
			document.documentElement.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
		}
		fullscreen.src = "/static/icons/shrink.png";
	} else {
		if (document.cancelFullScreen) {  
			document.cancelFullScreen();  
		} else if (document.mozCancelFullScreen) {  
			document.mozCancelFullScreen();  
		} else if (document.webkitCancelFullScreen) {  
			document.webkitCancelFullScreen();  
		}  
		fullscreen.src = "/static/icons/expand.png";
	}
}

function previousPage() {
	stopTranscode();
	window.history.back();
}

var hls;

function loadVideo() {
	if(Hls.isSupported()) {
		setTimeout(function(){ 
			config = Hls.DefaultConfig;
			config.autoStartLoad = true;
			config.startPosition = 0;
			config.debug = false;
			console.log(config);
			var player = document.getElementById('player');
			hls = new Hls(config);
			hls.attachMedia(player);

			hls.on(Hls.Events.MEDIA_ATTACHED, function () {
				hls.loadSource('/static/temp/' + m3u8 + '.m3u8');
				// Subtitle(s)
				player.addEventListener("loadedmetadata", function() { 
					prev_tracks = player.textTracks.length;
					for (i = 0; i < player.textTracks.length; i++) {
						player.textTracks[i].mode = "disabled";
					}
					for(i = 0; i < subtitle_language.length; i++) {
						track = document.createElement("track"); 
						track.kind = "captions";
						track.label = getLanguageName(subtitle_language[i]);
						track.srclang = subtitle_language[i];
						track.src = "/static/temp/" + m3u8 + "." + subtitle_language[i] + ".vtt"; 
						track.addEventListener("load", function() { 
							this.mode = "showing"; 
							player.textTracks[0].mode = "showing"; // thanks Firefox 
						}); 
						this.appendChild(track);
					}
					
				});
				hls.on(Hls.Events.MANIFEST_PARSED,function() {
					togglePlayPause();
				});
			});
			

			setTimeout(function(){ 
				console.log("load source");
				hls.levels;
			}, 5000); 


		}, 5000); 
	}
}
window.setInterval(function(){
	buffert_test();
}, 1000);

function buffert_test() {
	var video = document.getElementById('player');
	var buffered = video.buffered;
	console.log(
	  'The browser has buffered: ' + buffered.start(0) + ' - ' + buffered.end(0) + ' sec'
	);
}


window.onbeforeunload = function() {
	hls.destroy();
	stopTranscode();
};

function stopTranscode() {
	xhr = new XMLHttpRequest();
	xhr.open("POST", "/stop/" + m3u8, true);
	xhr.send(null);
}

function retranscode(time) {
	hls.destroy();
	xhr = new XMLHttpRequest();
	xhr.open("GET", "/retranscode/" + m3u8 + "/" + Math.floor(time), true);
	timeoffset = Math.floor(time);
	xhr.onload = function (e) {
		if (xhr.readyState === 4) {
			if (xhr.status === 200) {
				console.log(xhr.responseText);
				m3u8 = xhr.responseText;
				loadVideo();
			} else {
				console.error(xhr.statusText);
			}
		}
	};
	xhr.onerror = function (e) {
		console.error(xhr.statusText);
	};
	xhr.send(null);
}

