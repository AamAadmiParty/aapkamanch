var app = {};

$(function() {
	wn.datetime.refresh_when();
	
	$(".btn-post-add").on("click", function() {
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
	});
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
				console.log(data.exc)
			} else {
				app.render_authenticated_user(data.message)
			}
		}
	})
}

app.get_unit = function() {
	return decodeURIComponent(window.location.pathname.substr(1) || "india");
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
						app.render_authenticated_user(data);
					}
				})
			});
		} else {
			console.log('User cancelled login or did not fully authorize.');
		}
	},{scope:"email"});	
}