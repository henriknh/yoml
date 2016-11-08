function changeConfig(e) {

	config_id = e.getAttribute("configid");
	value_type = e.getAttribute("valuetype");
	value = e.getAttribute("value");

	// BOOL

	if(value_type == 'bool') {
		value = value * -1 + 1;
		e.setAttribute("value", value);

		if(value == 1) {
			e.src = '/static/icons/toggle-square-filled.png';
		} else {
			e.src = '/static/icons/toggle-square.png';
		}
	}
	
	// INT

	sendConfig(config_id, value);
}

function sendConfig(config_id, value) {
	xhr = new XMLHttpRequest();
	xhr.open("POST", "/setconfig/" + config_id + "/" + value, true);
	xhr.send(null);
}

function getConfigValue() {
	console.log("{{ config }}");
}