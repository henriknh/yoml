var images = new Array()
function preload() {
	for (i = 0; i < preload.arguments.length; i++) {
		images[i] = new Image()
		images[i].src = preload.arguments[i]
	}
}
preload(
	'/static/icons/close.png',
	'/static/icons/expand.png',
	'/static/icons/loading.gif',
	'/static/icons/pause.png',
	'/static/icons/play.png',
	'/static/icons/plus.png',
	'/static/icons/rating.png',
	'/static/icons/search.png',
	'/static/icons/settings.png',
	'/static/icons/shrink.png',
	'/static/icons/transparent.png',
	'/static/icons/volume-high.png',
	'/static/icons/volume-low.png',
	'/static/icons/volume-medium.png',
	'/static/icons/volume-mute.png'
)
window.onresize = function(event) {
    var dim_background = document.getElementById("dim_background");
    dim_background.style.minHeight = window.innerHeight + 'px';
    if (window.location.pathname.split('/').pop() == 'player') {
		document.getElementById("content").style.height = (window.innerHeight - 120) + 'px';
	} else {
		document.getElementById("content").style.height = (window.innerHeight - 80 - 70) + 'px';
	}
};

// Set minheight for no content
$(document).ready(function(){
	
});

/*
 	Menu
 */
var show_menu = false;
function toggle_menu() {
	if(show_menu) {
		$('#topNav').animate({height: '70px'}, 200);
	} else {
		$('#topNav').animate({height: '215px'}, 200);
	}
	show_menu = !show_menu;
	console.log(show_menu);
}


/*
	SEARCH
 */
function search_enter_key(e) {
    e = e || window.event;
    if (e.keyCode == 13){
    	search();
    }
}

function search() {
	query = encodeURI($("#search").val());

	if(query == '')
		return;

	xhr = new XMLHttpRequest();
	xhr.open("GET", "/search/" + query, true);
	xhr.onload = function (e) {
		if (xhr.readyState === 4) {
			if (xhr.status === 200) {
				handle_search(xhr.responseText);
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

function handle_search(data) {
	
	html = '';

	console.log('Handle search: ' + data);

	let jsonObject = JSON.parse(data);

	// movie
	for (i = 0; i < jsonObject[0].length; i++) {

	}

	// tvshow
	for (i = 0; i < jsonObject[1].length; i++) {

		tvshow_id = jsonObject[1][i]['tvshow_id'];
		SeriesName = jsonObject[1][i]['SeriesName'];
		FirstAired = jsonObject[1][i]['FirstAired'];
		FirstAired = FirstAired.split('-')[0];
		Rating = jsonObject[1][i]['Rating'];


		html += '<a href="/tvshows/' + tvshow_id + '" class="search_item">';
		html += 	'<img class="icon" src="/static/icons/tvshow.png">';
		html += 	'<div class="title">' + SeriesName + '</div>';
		html += 	'<div class="year left">' + FirstAired + '</div>';
		html += 	'<div class="rating right">' + Rating + '</div>';
		html += '</a>';

	}

	// episode
	/*for (i = 0; i < jsonObject[2].length; i++) {

		episode_id = jsonObject[2][i]['episode_id'];
		tvshow_id = jsonObject[2][i]['tvshow_id'];
		EpisodeName = jsonObject[2][i]['EpisodeName'];
		FirstAired = jsonObject[2][i]['FirstAired'];
		FirstAired = FirstAired.split('-')[0];
		Rating = jsonObject[2][i]['Rating'];


		html += '<a href="/tvshows/' + tvshow_id + '/' + episode_id + '" class="search_item">';
		html += 	'<img class="icon" src="/static/icons/tvshow.png">';
		html += 	'<div class="title">' + EpisodeName + '</div>';
		html += 	'<div class="year left">' + FirstAired + '</div>';
		html += 	'<div class="rating right">' + Rating + '</div>';
		html += '</a>';	
	}*/

	// picture
	for (i = 0; i < jsonObject[3].length; i++) {

	}

	$("#search_results").html(html);

	// .position() uses position relative to the offset parent, 
    // so it supports position: relative parent elements
    var pos = $('#search').position();

    // .outerWidth() takes into account border and padding.
    var width = $('#search').outerWidth();
    var height = $('#search').outerHeight();

    //show the menu directly over the placeholder
    $('#search_results').css({
    	display: 'block',
        position: 'absolute',
        top: (pos.top + height + 20) + 'px',
        left: (pos.left) + 'px'
    }).show();


}

$(document).mouseup(function (e)
{
    var container = $('#search_results');

    if (!container.is(e.target) // if the target of the click isn't the container...
        && container.has(e.target).length === 0) // ... nor a descendant of the container
    {
        container.hide();
    }
});

/*
	OTHER STUFF
 */


function leftPad(number, targetLength) {
    var output = number + '';
    while (output.length < targetLength) {
        output = '0' + output;
    }
    return output;
}


function setBackground(url, dim=true, frontpage=false, positonTop='70px') {
	if (url == undefined) {return;}

	var wrapper = document.getElementById("wrapper");
    var dim_background = document.getElementById("dim_background");
    wrapper.style.backgroundImage = "url('"+url+"')";
    wrapper.style.backgroundRepeat = "no-repeat";
    if(frontpage) {
    	wrapper.style.backgroundPosition = "center";
    } else {
    	wrapper.style.backgroundPosition = "center " + positonTop;
    }
    wrapper.style.backgroundAttachment = "fixed";
    if(dim) {
        dim_background.style.backgroundColor = "rgba(0, 0, 0, " + 0.7 + ")";
        dim_background.style.minHeight = window.innerHeight + 'px';
    }
}

$(document).ready(function() {
	$('#actors').click(function() {
	    var reducedHeight = $(this).height();
	    $(this).css('height', 'auto');
	    var fullHeight = $(this).height();
	    $(this).height(reducedHeight);

	    $(this).animate({height: fullHeight}, 500);
	});
});







function refresh_media() {
	xhr = new XMLHttpRequest();
	console.log(window.location.pathname.split('/').length);
	console.log(window.location.pathname.split('/').pop());
	if (window.location.pathname.split('/').length == 3) {
		xhr.open("POST", "/refresh_media/tvshow/" + window.location.pathname.split('/').pop());
	} else {
		xhr.open("POST", "/refresh_media/episode/" + window.location.pathname.split('/').pop());
	}
	xhr.send(null);
}

function toggle_media_watched(element) {
	
	console.log(element.src);

	xhr = new XMLHttpRequest();
	watched = element.src.indexOf('/watched') !== -1;
	if(watched) {
		console.log('Mark ' + window.location.pathname.split('/').pop() + ' as watched');
		watched = 1;
		$(element).attr('src', '/static/icons/unwatched.png');
	} else {
		console.log('Mark ' + window.location.pathname.split('/').pop() + ' as unwatched');
		watched = 0;
		$(element).attr('src', '/static/icons/watched.png');
	}
	if (window.location.pathname.split('/').length == 3) {
		xhr.open("POST", "/toggle_media_watched/tvshow/" + window.location.pathname.split('/').pop() + "/" + watched);
	} else {
		xhr.open("POST", "/toggle_media_watched/episode/" + window.location.pathname.split('/').pop() + "/" + watched);
	}
	xhr.send(null);

}

function remove_media() {

	check = confirm("Are you sure you want remove tvshow?");
	if (check == true) {
		xhr = new XMLHttpRequest();
		if (window.location.pathname.split('/').length == 3) {
			xhr.open("POST", "/remove_media/tvshow/" + window.location.pathname.split('/').pop());
		} else {
			xhr.open("POST", "/remove_media/episode/" + window.location.pathname.split('/').pop());
		}
		xhr.send(null);

		window.location.replace(window.location.href.substr(0, window.location.href.lastIndexOf("/")));
    }
}