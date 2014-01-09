// AAP Ka Manch, License GNU General Public License v3

$(function() {
	$(".btn-post-add").on("click", app.add_post);
	$(".feed").on("click", ".btn-post-settings", function() {
		app.toggle_post_settings.apply(this);
	})
})

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
			cmd: "aapkamanch.post.add_post",
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

app.toggle_post_settings = function() {
	var $btn = $(this),
		$post = $btn.parents(".post:first"),
		$post_settings = $(".post-settings");

	if($post_settings.parents(".post:first").attr("data-name") === $post.attr("data-name")) {
		$post_settings.remove();
		return;
	} else {
		$post_settings.remove();
		$btn.prop("disabled", true);
		$.ajax({
			url: "/",
			data: {
				cmd: "aapkamanch.post.get_post_settings",
				post_name: $post.attr("data-name"),
				unit: $post.attr("data-unit")
			},
			success: function(data) {
				$btn.prop("disabled", false);
				if(data.exc) {
					console.log(data.exc);
				} else {
					app.setup_post_settings($post, data.message);
				}
			}
		});
	}
}

app.setup_post_settings = function($post, post_settings_html) {
	var $post_settings = $(post_settings_html).appendTo($post.find(".post-settings-area"));

	var $control_event = $post_settings.find(".control-event").empty();
	app.setup_datepicker({
		$control: $control_event
	});
	
	// set event
	
	
	// assign events
	var $control_assign = $post_settings.find(".control-assign").empty();
	if($control_assign.length) {
		app.setup_autosuggest({
			$control: $control_assign,
			select: function(value) {
				app.assign_post($post, value, $control_assign);
			},
			method: "aapkamanch.post.suggest_user"
		});
	} else {
		$post_settings.find("a.close").on("click", function() {
			app.assign_post($post, null, $(this));
		});
	}
}

app.assign_post = function($post, profile, $control) {
	var post_name = $post.attr("data-name");
	$control.prop("disabled", true);
	$.ajax({
		url: "/",
		type: "POST",
		data: {
			cmd: "aapkamanch.post.assign_post",
			post: $post.attr("data-name"),
			profile: profile
		},
		statusCode: {
			403: function(xhr) {
				wn.msgprint("Not Permitted");
			},
			200: function(data) {
				if(data._server_messages) {
					wn.msgprint(JSON.parse(data._server_messages).join("\n"));
				} else {
					$(".post-settings").remove();
					app.setup_post_settings($post, data.message.post_settings_html);
					var fullname = data.message.assigned_to_fullname || "";
					$post.find(".assigned-label")
						.html(fullname || "")
						.toggleClass("hide", !fullname);
				}
			}
		}
	}).always(function() {
		$control.val("").prop("disabled", false);
	});
};