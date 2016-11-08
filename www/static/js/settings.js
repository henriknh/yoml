function change_checkbox_value(config, config_id) {
	if (config.checked == true) {
		document.getElementById(config_id).setAttribute("value", "0");
	} else {
		document.getElementById(config_id).setAttribute("value", "1");
	}
}

//
//	GENERAL
//

function test_port_enter_key(e)
{
    e = e || window.event;
    if (e.keyCode == 13){
    	document.getElementById('test_port').click();
    }
}

function test_port() {
	
	port = document.getElementById("general_flask_port").value;

	document.getElementById("test_port_result").style.background = "url('/static/icons/loading.gif')";
    document.getElementById("test_port_result").style.backgroundSize = "32px 32px";
    document.getElementById("test_port_result_text").innerHTML = '';

	xhr = new XMLHttpRequest();
	xhr.open("GET", "/test_port/" + encodeURI(port), true);
	xhr.onload = function (e) {
		if (xhr.readyState === 4) {
			if (xhr.status === 200) {
				if (xhr.responseText == 1) {
					document.getElementById("test_port_result").style.background = "url('/static/icons/access.png')";
    				document.getElementById("test_port_result").style.backgroundSize = "32px 32px";
    				document.getElementById("test_port_result_text").innerHTML = 'Port is accessable from outside network';
				} else {
					document.getElementById("test_port_result").style.background = "url('/static/icons/error.png')";
    				document.getElementById("test_port_result").style.backgroundSize = "32px 32px";
    				document.getElementById("test_port_result_text").innerHTML = 'Port is blocked from outside network';
				}
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



//
//	MANAGE MEDIA
//
$(document).ready(function() {
	if(window.location.pathname.split('/')[2] == 'manage') {
		get_filetree();
	}
});
function get_filetree(path) {
	if (path == undefined) {
		path = 'root';
	}
	xhr = new XMLHttpRequest();
	xhr.open("GET", "/filetree/" + encodeURI(path), true);
	xhr.onload = function (e) {
		if (xhr.readyState === 4) {
			if (xhr.status === 200) {
				populate_filetree(xhr.responseText);
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

function populate_filetree(folders) {
	folders = JSON.parse(folders);
	filetree_current = document.getElementById("filetree_current_path").value = folders[0][0];
	filetree = document.getElementById("filetree_browser");
	filetree.innerHTML = '';

	for (var i = 1; i < folders.length; i++) {
	    
	    s = '<div class="item pointer ';
	    if (i % 2 == 0) {
	    	s += 'lightgray" onclick="get_filetree(\'' + folders[i][0] + '\');">';
	    } else {
	    	s += 'gray" onclick="get_filetree(\'' + folders[i][0] + '\');">';
	    }
	    if(folders[i][1] == '..') {
	    	s += '<img src="/static/icons/return.png">';
	    } else {
	    	s += '<img src="/static/icons/folder.png">';
	    }
	    s += folders[i][1] + '</div>';
	    
	    filetree.innerHTML += s;
	}
}

function remove_library(element) {
	id = element.getAttribute("libraryid");
	xhr = new XMLHttpRequest();
	xhr.open("POST", "/remove_library/" + id, true);
	xhr.send(null);
	element.parentElement.parentElement.style.display = 'none';
}



//
//	DOWNLOAD CLIENT
//
function download_client_change() {
	console.log("asd");

	//$('#txtEntry2').val($(this).find(":selected").text());
	console.log($(this).find(":selected").text());

}
