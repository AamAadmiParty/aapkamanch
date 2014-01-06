var app = {};

app.setup_user = function(data) {
	// user
	data.cmd = "aapkamanch.helpers.get_user_details";
	data.unit = app.get_unit();
	$.ajax({
		url: "/",
		data: data,
		success: function(data) {
			if(data.exc){
				console.log(data.exc)
			} else {
				app.render_authenticated_user(data)
			}
		}
	})
}

app.get_unit = function() {
	return window.location.pathname.substr(1) || "india";
}

app.render_authenticated_user = function(data) {
	// render private groups
	// render editor / add button if has access
}

function get_cookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}
