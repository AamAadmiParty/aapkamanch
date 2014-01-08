// AAP Ka Manch, License GNU General Public License v3

$(function() {
	$(".btn-post-add").on("click", app.add_post);
	$(".feed").on("click", ".btn-post-settings", app.toggle_post_settings)
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
	// hide if exists
	var $post = $(this).parents(".post:first");
	var $post_settings = $(".post-settings");

	if($post_settings.parents(".post:first").attr("data-name") === $post.attr("data-name")) {
		$post_settings.remove();
		return;
	} else {
		$post_settings.remove();
		$.ajax({
			url: "/",
			data: {
				cmd: "aapkamanch.post.get_post_settings",
				post_name: $post.attr("data-name"),
				unit: app.get_unit()
			},
			success: function(data) {
				if(data.exc) {
					console.log(data.exc);
				} else {
					app.setup_post_settings($post, data);
				}
			}
		});
	}
}

app.setup_post_settings = function($post, data) {
	var $post_settings = $(data.message).appendTo($post.find(".post-settings-area"));

	var $control_event = $post_settings.find(".control-event").empty();
	var $control_assign = $post_settings.find(".control-assign").empty();

	app.setup_datepicker({
		$control: $control_event
	});
	
	if($post_settings.find(".control-assign").length) {
		app.setup_autosuggest({
			$control: $control_assign,
			select: function(value) {
				app.set_in_post($post, "assigned_to", value);
			},
			method: "aapkamanch.post.suggest_user"
		});
	} else {
		$post_settings.find("a.close").on("click", function() {
			app.assign_to_profile($post, null);
		});
	}
}

app.set_in_post = function($post, fieldname, value) {
	$.ajax({
		url: "/",
		type: "POST",
		data: {
			cmd: "aapkamanch.post.set_in_post",
			post: $post.attr("data-name"),
			fieldname: fieldname,
			value: value
		},
		success: function(data) {
			$(".post-settings").remove();
			app.setup_post_settings($post, data);
		}
	});
}