// AAP Ka Manch, License GNU General Public License v3

var app = {};

$(function() {
	wn.datetime.refresh_when();
	
	$(".titlebar .toggle-sidebar").on("click", function() {
		$(".sidebar").toggleClass("hidden-xs");
	})
});

app.setup_user = function(data) {
	// user
	data.cmd = "aapkamanch.helpers.get_user_details";
	data.unit = app.get_unit();
	$.ajax({
		url: "/",
		data: data,
		success: function(data) {
			if(data.exc){
				console.log(data.exc);
			} else {
				if(data.session_expired) {
					wn.msgprint("Session Expired");
					setTimeout(function() { window.location.reload() }, 2000);
				}
				app.render_authenticated_user(data.message);
			}
		}
	});
}

app.render_authenticated_user = function(data) {
	$(".btn-login-area").toggle(false);
	$(".logged-in").toggle(true);
	$(".full-name").html(wn.get_cookie("full_name"));
	$(".user-picture").attr("src", data.user_image)

	// hide editor / add button if no access
	if(data.access && data.access.write) {
		$(".tab-add").removeClass("hide");
	}
	
	if(data.access && data.access.admin) {
		$(".tab-settings").removeClass("hide");
	}

	// render private groups
	if(data.private_units) {
		$(data.private_units).prependTo(".unit-list-group");
	}
	
	app.show_cannot_post_message(data.access);
}

app.show_cannot_post_message = function(access, message) {
	if(!(access && access.write)) {
		$(".post-list-help").html(message || "You do not have permission to post");
	}
}

app.setup_autosuggest = function(opts) {
	if(opts.$control.hasClass("ui-autocomplete-input")) return;
	
	wn.require("/assets/webnotes/js/lib/jquery/jquery.ui.min.js");
	wn.require("/assets/webnotes/js/lib/jquery/bootstrap_theme/jquery-ui.selected.css");

	var $user_suggest = opts.$control.autocomplete({
		source: function(request, response) {
			$.ajax({
				url: "/",
				data: {
					cmd: opts.method,
					term: request.term,
					unit: app.get_unit()
				},
				success: function(data) {
					if(data.exc) {
						console.log(data.exc);
					} else {
						response(data.message);
					}
				}
			});
        },
		select: function(event, ui) {
			opts.$control.val("");
			opts.select(ui.item.profile);
		}
	});
	
	$user_suggest.data( "ui-autocomplete" )._renderItem = function(ul, item) {
		return $("<li>").html("<a style='padding: 5px;'>" + item.profile_html + "</a>")
			.css("padding", "5px")
			.appendTo(ul);
    };
	
	return opts.$control
};

app.setup_datepicker = function(opts) {
	if(opts.$control.hasClass("hasDatetimepicker")) return;
	
	// libs required for datetime picker
	wn.require("/assets/webnotes/js/lib/jquery/jquery.ui.min.js");
	wn.require("/assets/webnotes/js/lib/jquery/bootstrap_theme/jquery-ui.selected.css");
	wn.require("/assets/webnotes/js/lib/jquery/jquery.ui.slider.min.js");
	wn.require("/assets/webnotes/js/lib/jquery/jquery.ui.sliderAccess.js");
	wn.require("/assets/webnotes/js/lib/jquery/jquery.ui.timepicker-addon.css");
	wn.require("/assets/webnotes/js/lib/jquery/jquery.ui.timepicker-addon.js");	

	opts.$control.datetimepicker({
		timeFormat: "hh:mm tt",
		dateFormat: 'dd-mm-yy',
		changeYear: true,
		yearRange: "-70Y:+10Y",
		stepMinute: 5,
		hour: 10,
		onClose: opts.onClose
	});
	
	app.setup_datetime_functions();
	
	return opts.$control;
}

app.get_unit = function() {
	return window.app.unit || "india";
};

app.get_view = function() {
	return window.app.view;
}

app.logout = function() {
	$.ajax({
		type:"POST",
		url:"/",
		data: {
			cmd:"logout" 
		},
		success: function() {
			window.location.reload();
		}
	})
}

app.login_via_facebook = function() {
	// not logged in to facebook either
	FB.login(function(response) {
	   if (response.authResponse) {
		   // yes logged in via facebook
		   console.log('Welcome!  Fetching your information.... ');
		   var fb_access_token = response.authResponse.accessToken;

		   // get user graph
		   FB.api('/me', function(response) {
			   response.fb_access_token = fb_access_token || "[none]";
			   response.unit = app.get_unit();
			   $.ajax({
					url:"/",
					type: "POST",
					data: {
						cmd:"aapkamanch.helpers.add_user",
						data: JSON.stringify(response)
					},
					success: function(data) {
						if(data.exc) console.log(data.exc);
						window.location.reload();
					}
				})
			});
		} else {
			wn.msgprint("You have denied access to this application via Facebook. \
				Please change your privacy settings in Facebook and try again. \
				If you do not want to use Facebook login, <a href='/login'>sign-up</a> here");
		}
	},{scope:"email"});	
}

app.setup_datetime_functions = function() {
	// requires datetime picker
	wn.provide("app.datetimepicker");
	app.datetimepicker.str_to_obj = function(datetime_str) {
		return $.datepicker.parseDateTime("yy-mm-dd", "HH:mm:ss", datetime_str);
	};

	app.datetimepicker.obj_to_str = function(datetime) {
		if(!datetime) {
			return "";
		}
		// requires datepicker
		var date_str = $.datepicker.formatDate("yy-mm-dd", datetime)
		var time_str = $.datepicker.formatTime("HH:mm:ss", {
			hour: datetime.getHours(),
			minute: datetime.getMinutes(),
			second: datetime.getSeconds()
		})
		return date_str + " " + time_str;
	};

	app.datetimepicker.format_datetime = function(datetime) {
		if (typeof(datetime)==="string") {
			datetime = app.datetimepicker.str_to_obj(datetime);
		}
		var date_str = $.datepicker.formatDate("dd-mm-yy", datetime)
		var time_str = $.datepicker.formatTime("hh:mm tt", {
			hour: datetime.getHours(),
			minute: datetime.getMinutes(),
			second: datetime.getSeconds()
		})
		return date_str + " " + time_str;
	}
}
