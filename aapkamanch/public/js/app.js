// AAP Ka Manch, License GNU General Public License v3

var app = {};

$(function() {
	wn.datetime.refresh_when();
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
	})
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
		timeFormat: "hh:mm:ss",
		dateFormat: 'dd-mm-yy',
		changeYear: true,
		yearRange: "-70Y:+10Y"
	})
	return opts.$control;
}

app.toggle_date_format = function(datetime) {
	if(!datetime) return "";
	var date = datetime.split(" ")[0].split("-");
	var time = datetime.split(" ")[1];
	return [date[2], date[1], date[0]].join("-") + " " + time;
}

app.get_unit = function() {
	return window.app.unit || "india";
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
			console.log('User cancelled login or did not fully authorize.');
		}
	},{scope:"email"});	
}