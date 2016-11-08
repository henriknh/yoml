//
//	MODAL
//

var modal = document.getElementById('myModal');
var span = document.getElementsByClassName("close")[0];

function display_modal() {
    document.getElementById('myModal').style.display = "block";
	document.getElementById("modal_search").focus();

	getLibrariesForModal();
	modal_current_body = 1;
	modalNavigation();
}

function close_modal() {
    document.getElementById('myModal').style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == document.getElementById('myModal')) {
        close_modal();
    }
}

/*
 *	Change media type tab
 */


$(document).ready(function() {
	$("input[name=newmedia]:radio").change(function () {
		$('#modal_search').val('');
		document.getElementById("modal_search_results").innerHTML = '';
		document.getElementById("modal_search").focus();
		modal_current_body = 1;
		modalNavigation();

		if($('input[name="newmedia"]:checked').val() == 'tvshow') {
			document.getElementById('modal_search').placeholder='Search for TV Show';
		}
		if($('input[name="newmedia"]:checked').val() == 'movie') {
			document.getElementById('modal_search').placeholder='Search for Movie';
		}
	});
});

/*
 *	Change selected (radio buttons) media 
 */

$(document).ready(function() {
	$("input[name=modal_result]:radio").change(function () {
		console.log("rofl");
	});
});

/*
 *	SEARCH MODAL
 */

function searchTestKeyPress(e){
    // look for window.event in case event isn't passed in
    e = e || window.event;
    if (e.keyCode == 13)
    {
        document.getElementById('btn_modal_search').click();
        return false;
    }
    return true;
}

function searchTVShowMovie() {

	query = $('#modal_search').val().trim();

	if(query == '')
		return
	
	if($('input[name="newmedia"]:checked').val() == 'tvshow') {
		url = "/searchtvshow/" + query;
		type = 'tvshow';
	}
	if($('input[name="newmedia"]:checked').val() == 'movie') {
		url = "/searchmovie/" + query;
		type = 'movie';
	}

	xhr = new XMLHttpRequest();
	xhr.open("GET", url, true);
	xhr.onload = function (e) {
	    if (xhr.readyState === 4) {
	        if (xhr.status === 200) {
	            populateModal(xhr.responseText, type);
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

function populateModal(data, type) {

	parser = new DOMParser();
	xmlDoc = parser.parseFromString(data,"text/xml");

	if(type = 'tvshow') {

		html = ''
		for (i = 0; i < xmlDoc.childNodes[0].childElementCount; i++) {
			if(i % 2 == 0) {
				color = '#707070';
			} else {
				color = '#606060';
			}

			if (xmlDoc.getElementsByTagName("seriesid")[i] == null ||
				xmlDoc.getElementsByTagName("SeriesName")[i] == null ||
				xmlDoc.getElementsByTagName("FirstAired")[i] == null) 
			{
				break;
			}

			html += '<input id="modal_result_data' + i + '" type="radio" name="modal_result" value="' + xmlDoc.getElementsByTagName("seriesid")[i].childNodes[0].nodeValue + '" />';
	      	html += '<label class="modal_result_label" for="modal_result_data' + i + '" style="background-color: ' + color + ';">';
	      	html += '	<img class="icon" src="/static/icons/tvshow.png" />';
	        html += '	<div class="name">' + xmlDoc.getElementsByTagName("SeriesName")[i].childNodes[0].nodeValue + '</div>';
	        html += '	<a class="url" href="http://thetvdb.com/?tab=series&id=' + xmlDoc.getElementsByTagName("seriesid")[i].childNodes[0].nodeValue + '" target="_blank"><img class="icon" src="/static/icons/www.png" /></a>';
	        html += '	<div class="year">' + xmlDoc.getElementsByTagName("FirstAired")[i].childNodes[0].nodeValue.split("-")[0] + '</div>';
	      	html += '</label>';

		}

		document.getElementById("modal_search_results").innerHTML = html;
	}
	if(type = 'movie') {

	}
}


/*
 *	GET LIBRARIES FOR MODAL
 */

var modal_libraries;
function getLibrariesForModal() {

	xhr = new XMLHttpRequest();
	xhr.open("GET", "/getlibrariesformodal", true);
	xhr.onload = function (e) {
		if (xhr.readyState === 4) {
			if (xhr.status === 200) {
				modal_libraries = xhr.responseText;
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


/*
 *	DISPLAY LIBRARIES DATA IN MODAL
 */

function populateLibrariesModal() {

	parser = new DOMParser();
	xmlDoc = parser.parseFromString(modal_libraries,"text/xml");

	if($('input[name="newmedia"]:checked').val() == 'tvshow') {
		type = 'tvshows';
	}
	if($('input[name="newmedia"]:checked').val() == 'movie') {
		type = 'movies';
	}

	html = ''

	// count how many of each type
	count_library_tvshows = 0;
	count_library_movies = 0;
	for (i = 0; i < xmlDoc.childNodes[0].childElementCount; i++) {
		if(xmlDoc.getElementsByTagName("type")[i].childNodes[0].nodeValue == 'tvshows') {
			count_library_tvshows++;
		}
		if(xmlDoc.getElementsByTagName("type")[i].childNodes[0].nodeValue == 'movies') {
			count_library_movies++;
		}
	}
	
	// Display error in modal if no library exists for that type
	if(type == 'tvshows' && count_library_tvshows == 0) {
	    html += "There doesn't seem to be any libraries for TV Shows. Add one in Settings.";
	    document.getElementById("modal_libraries").innerHTML = html;
		return;
	    } 
	if(type == 'movies' && count_library_movies == 0) {
	    html += "There doesn't seem to be any libraries for Movies. Add one in Settings.";
	    document.getElementById("modal_libraries").innerHTML = html;
		return;
	}

	for (i = 0; i < xmlDoc.childNodes[0].childElementCount; i++) {
		if(i % 2 == 0) {
			color = '#707070';
		} else {
			color = '#606060';
		}

		if(xmlDoc.getElementsByTagName("type")[i].childNodes[0].nodeValue == type) {

			html += '<input id="modal_library_data' + i + '" type="radio" name="modal_library" value="' + xmlDoc.getElementsByTagName("library_id")[i].childNodes[0].nodeValue + '" />';
	      	html += '<label class="modal_library_label" for="modal_library_data' + i + '" style="background-color: ' + color + ';">';
	      	if(type == 'tvshows') {
	      		html += '	<img class="icon" src="/static/icons/tvshow.png" />';
	      	} else {
	      		html += '	<img class="icon" src="/static/icons/movie.png" />';
	      	}
	        html += '	<div class="name">' + xmlDoc.getElementsByTagName("path")[i].childNodes[0].nodeValue + '</div>';
	        html += '</label>';
		}
		
		document.getElementById("modal_libraries").innerHTML = html;	
	}

	$('input[name="modal_library"]:first').attr('checked', true);
}

/*
 *	MODAL PREV OR NEXT NAVIGATION
 */

var modal_current_body = 1;

function modalNavigation(direction) {

	modal_prev = document.getElementById("btn_modal_prev");
	modal_next = document.getElementById("btn_modal_next");
	modal_bodies = [document.getElementById("modal-body-1"), document.getElementById("modal-body-2"), document.getElementById("modal-body-3")];

	// Run submit-function
	if(modal_current_body == 3 && direction == 'next') {
		submitNewMedia();
		return;
	}

	// Change page
	if(direction == 'prev') {
		modal_current_body--;
		if(modal_current_body < 1)
			modal_current_body = 1
	}
	if(direction == 'next') {
		modal_current_body++;
		if(modal_current_body > 3)
			modal_current_body = 3
	}

	// Display button(s)
	if(modal_current_body != 1) {
		modal_prev.style.display = 'inline-block';
	} else {
		modal_prev.style.display = 'none';	
	}

	// Change button text
	if(modal_current_body == 3) {
		modal_next.innerHTML = 'Submit';
	} else {
		modal_next.innerHTML = 'Next';
	}

	// Display correct body
	if(modal_current_body == 1) {
		modal_bodies[0].style.display = 'block';
		modal_bodies[1].style.display = 'none';
		modal_bodies[2].style.display = 'none';
	}
	if(modal_current_body == 2) {
		modal_bodies[0].style.display = 'none';
		modal_bodies[1].style.display = 'block';
		modal_bodies[2].style.display = 'none';
		populateLibrariesModal();
	}
	if(modal_current_body == 3) {
		modal_bodies[0].style.display = 'none';
		modal_bodies[1].style.display = 'none';
		modal_bodies[2].style.display = 'block';
	}
}

/*
 *	SUBMIT NEW MEDIA TO SERVER
 */

function submitNewMedia() {

	type = $('input[name="newmedia"]:checked').val();
	media = $('input[name="modal_result"]:checked').val();
	library_id = $('input[name="modal_library"]:checked').val();

	if(media == undefined) {
		console.log('Error! No media in modal selected!');
		close_modal();
		return;
	}

	if(library_id == undefined) {
		console.log('Error! No library in modal selected! (Most likely no library for ' + type + ' on server)');
		close_modal();
		return;
	}

	xhr = new XMLHttpRequest();
	xhr.open("POST", "/new_media/" + type + "/" + media + "/" + library_id , true);
	xhr.send(null);

	close_modal();
}