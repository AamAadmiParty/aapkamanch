var app = {};

$(function() {
	wn.datetime.refresh_when();
	$(".btn-post-add").on("click", app.add_post);
	$(".btn-settings").on("click", app.toggle_settings);
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
	$(".user-picture").attr("src", "http://graph.facebook.com/" + data.fb_username + "/picture")

	// render editor / add button if has access
	if(data.access.write) {
		$(".feed-editor").toggle(true);
	}

	// render private groups
	if(data.private_units) {
		$(data.private_units).prependTo(".unit-list-group")
	}
	
	if(data.access.admin) {
		$(".btn-settings").toggle(true);
	}
}

app.get_unit = function() {
	return decodeURIComponent(window.location.pathname.substr(1) || "india");
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

app.add_post = function() {
	var btn = this;
	$(btn).prop("disabled", true);
	var content = $(".post-add-control").val();
	if(!content) {
		wn.msgprint("Please enter some text!");
		return;
	}
	$.ajax({
		type: "POST",
		url: "/",
		data: {
			cmd: "aapkamanch.aapkamanch.doctype.post.post.add_post",
			unit: app.get_unit(),
			content: content
		},
		success: function(data) {
			$(btn).prop("disabled", false);
			if(data.exc){
				console.log(data.exc);
			} else {
				$(".post-add-control").val("");
				$(data.message).prependTo($(".post-list"));
				wn.datetime.refresh_when();
			}
		}
	})	
};

app.toggle_settings = function() {
	if(app.settings_shown) {
		$(".permission-editor-area").toggle(false);
		app.settings_shown = false;
	} else {
		if(!app.settings_loaded) {
			wn.require("assets/webnotes/js/lib/jquery/jquery.ui.min.js");
			wn.require("assets/webnotes/js/lib/jquery/bootstrap_theme/jquery-ui.selected.css");
			$.ajax({
				url:"/",
				data: {
					cmd: "aapkamanch.helpers.get_permission_html",
					unit: app.get_unit()
				},
				success: function(data) {
					if(data.exc) 
						console.log(data.exc)
					$(".permission-editor-area").toggle(true)
						.empty().html(data.message);
					app.settings_loaded = true;
					
					app.setup_autosuggest($(".add-user-control"));
					$(".permission-editor-area").on("click", "[type='checkbox']", app.update_permission)
				}
			})
		} else {
			$(".permission-editor-area").toggle(true);
		}
		app.settings_shown = true;
	}
}

app.setup_autosuggest = function($control) {
	var $user_suggest = $control.autocomplete({
		source: function(request, response) {
			$.ajax({
				url: "/",
				data: {
					cmd: "aapkamanch.helpers.suggest_user",
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
			$control.val("");
			app.add_unit_profile(ui.item.value);
		}
	});
	
	$user_suggest.data( "ui-autocomplete" )._renderItem = function(ul, item) {
		return $("<li>").html("<a style='padding: 5px;'>" + item.profile_html + "</a>")
			.css("padding", "5px")
			.appendTo(ul);
    };
};

app.update_permission = function() {
	var $chk = $(this);
	var $tr = $chk.parents("tr:first");
	$chk.prop("disabled", true);
	
	$.ajax({
		url: "/",
		type: "POST",
		data: {
			cmd: "aapkamanch.helpers.update_permission",
			profile: $tr.attr("data-profile"),
			perm: $chk.attr("data-perm"),
			value: $chk.prop("checked") ? "1" : "0",
			unit: app.get_unit()
		},
		success: function(data) {
			$chk.prop("disabled", false);
			if(data.exc) {
				$chk.prop("checked", !$chk.prop("checked"));
				console.log(data.exc);
			} else {
				if(!$tr.find(":checked").length) $tr.remove();
			}
		}
	});
}

app.add_unit_profile = function(profile) {
	$.ajax({
		url: "/",
		type: "POST",
		data: {
			cmd: "aapkamanch.helpers.add_unit_profile",
			profile: profile,
			unit: app.get_unit()
		},
		success: function(data) {
			$(".add-user-control").val("");
			if(data.exc) {
				console.log(data.exc);
			} else {
				$(data.message).prependTo($(".permission-editor tbody"));
			}
		}
	});
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
						app.render_authenticated_user(data);
					}
				})
			});
		} else {
			console.log('User cancelled login or did not fully authorize.');
		}
	},{scope:"email"});	
}