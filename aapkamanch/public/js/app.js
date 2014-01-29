// AAP Ka Manch, License GNU General Public License v3

wn.provide("app");

$(function() {
	$('.dropdown-toggle').dropdown();
	wn.datetime.refresh_when();
	
	$(".toggle-sidebar").on("click", function() {
		$(".sidebar").toggleClass("hidden-xs");
		$(".toggle-sidebar i").toggleClass("icon-rotate-180");
	});
	
	// bind push and pop state
	app.bind_state_change()
});

app.bind_state_change = function() {
	if(history.pushState) {
		$(document).on("click", "#content a", function() {
			var href = $(this).attr("href");
			if(href.indexOf("/")===0) {
				// console.log("pushstate!");
				app.get_content(href);
				return false;
			}
		});
		
		$(window).on("popstate", function(event) {
			if(!event.originalEvent.state) return;
			var data = event.originalEvent.state.data;
			if(data) {
				$("#content").html(data.content);
				app.toggle_based_on_permissions(data);
			} else {
				history.go();
			}
		})
	}
};

app.get_content = function(href) {
	history.pushState(null, null, href);
	$.ajax({
		url: href,
		data: {
			cmd: "aapkamanch.templates.pages.index.fetch_content"
		},
		statusCode: {
			200: function(data) {
				// for use in popstate event
				history.replaceState({"data": data.message}, null, href);
				
				$("#content").html(data.message.content);
				app.toggle_based_on_permissions(data.message);
			}
		}
	}).always(function(data) {
		if(data.responseText) {
			data = JSON.parse(data.responseText);
		}
		if(data.exc) {
			console.log(JSON.parse(data.exc).join("\n"));
		}
	});
}

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
				app.toggle_based_on_permissions(data.message);
			}
		}
	});
}

app.render_authenticated_user = function(data) {
	$(".btn-login-area").toggle(false);
	$(".logged-in").toggle(true);
	$(".full-name").html(wn.get_cookie("full_name"));
	$(".user-picture").attr("src", data.user_image)
};

app.toggle_based_on_permissions = function(data) {
	// hide editor / add button if no access
	if(data.access && data.access.write) {
		$('li[data-view="add"]').removeClass("hide");
	}
	
	if(data.access && data.access.admin) {
		$('li[data-view="settings"]').removeClass("hide");
	}

	// render private groups
	if(data.private_units) {
		$(data.private_units).prependTo(".unit-list-group");
	}
	
	app.show_cannot_post_message(data.access);
	
	wn.datetime.refresh_when();
}

app.setup_upvote = function() {
	$(".post-list, .parent-post").on("click", ".upvote a", function() {
		var sid = wn.get_cookie("sid");
		if(!sid || sid==="Guest") {
			wn.msgprint("Please login to Upvote!");
			return;
		}
		
		var $btn = $(this).prop("disabled", true);
		var $post = $(this).parents(".post");
		var post = $post.attr("data-name");
		$.ajax({
			url: "/",
			type: "POST",
			data: {
				cmd: "aapkamanch.vote.set_vote",
				ref_doctype: "Post",
				ref_name: post
			},
			statusCode: {
				200: function(data) {
					if(data.exc) {
						console.log(data.exc);
					} else {
						var text_class = data.message === "ok" ? "text-success" : "text-danger";
						if(data.message==="ok") {
							var count = parseInt($post.find(".upvote-count").text());
							$post.find(".upvote-count").text(count + 1).removeClass("hide");
						}
						$btn.addClass(text_class);
						setTimeout(function() { $btn.removeClass(text_class); }, 2000);
					}
				}
			}
		}).always(function() {
			$btn.prop("disabled", false);
		})
	});
};

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
			opts.select(ui.item.profile, ui.item);
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
};

app.setup_more_btn = function(opts, prepend) {
	$(".btn-more").on("click", function() {
		$(this).prop("disabled", true);
		var limit_start = $(".post").length;
		if(!opts) opts = {};
		$.ajax({
			url: "/",
			data: $.extend(opts, {
				unit: app.get_unit(),
				view: app.get_view(),
				limit_start: limit_start,
			}),
			statusCode: {
				403: function(xhr) {
					wn.msgprint("Not Permitted");
				},
				200: function(data) {
					if(data.exc) {
						console.log(JSON.parse(data.exc).join("\n"));
					} else {
						if(prepend) {
							$(".post-list").prepend(data.message);
						} else {
							$(".post-list").append(data.message);
						}
						wn.datetime.refresh_when();
						app.format_event_timestamps();
						app.show_more_btn(limit_start);
						app.toggle_edit();
						app.toggle_upvote();
					}
				}
			}
		}).always(function() {
			$(this).prop("disabled", false);
		})
	});
	app.show_more_btn(0);
};

app.show_more_btn = function(limit_start, limit_length) {
	var show_more_btn = ($(".post").length - (limit_start || 0)) === (limit_length || 20);
	$(".btn-more").toggleClass("hide", !show_more_btn);
}