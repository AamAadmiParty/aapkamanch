// AAP Ka Manch, License GNU General Public License v3

$(function() {
	$pic_input = $(".control-post-add-picture");
	$(".btn-post-add").on("click", app.add_post);
	$(".btn-post-add-picture").on("click", function() { 
		$pic_input.click();
	});
	$pic_input.on("change", app.add_picture)
	$(".feed").on("click", ".btn-post-settings", function() {
		app.toggle_post_settings.apply(this);
	});
	app.format_event_timestamps();
})

app.add_post = function() {
	var btn = this;
	var content = $(".post-add-control").val();
	if(!content) {
		wn.msgprint("Please enter some text!");
		return;
	}
	var dataurl = $(".post-picture img").attr("src");
	
	// convert links in content
	content = app.process_external_links(content);
	
	$(btn).prop("disabled", true);
	$.ajax({
		type: "POST",
		url: "/",
		data: {
			cmd: "aapkamanch.post.add_post",
			unit: app.get_unit(),
			content: content,
			picture_name: $(".control-post-add-picture").val(),
			picture: dataurl ? dataurl.split(",")[1] : "",
			parent_post: $(".post-editor").attr("data-parent-post") 
		},
		success: function(data) {
			if(data.exc){
				console.log(data.exc);
			} else {
				$(".post-add-control").val("");
				$(".post-picture").toggle(false).find("img").attr("src", "");
				$(data.message).prependTo($(".post-list"));
				wn.datetime.refresh_when();
				app.format_event_timestamps();
			}
		}
	}).always(function() {
		$(btn).prop("disabled", false);
	})
};

app.add_picture = function() {
	if (this.type === 'file' && this.files && this.files.length > 0) {
		$.each(this.files, function (idx, fileobj) {
			if (/^image\//.test(fileobj.type)) {
				var reader = new FileReader();
				reader.onload = function() {
					// resize
					var tmp = new Image();
					tmp.src = reader.result;
					tmp.onload = function() {
						var w = tmp.width, h = tmp.height;
						if(tmp.width > 500) {
							w = 500; h = h * (500.0 / tmp.width);
						}
						var canvas = document.createElement('canvas');
						canvas.width = w; canvas.height = h;
						var ctx = canvas.getContext("2d");
						ctx.drawImage(this, 0, 0, w, h);
						var dataurl = canvas.toDataURL("image/jpeg");
						$(".post-picture").toggle(true).find("img").attr("src", dataurl);
					}
				};
				reader.readAsDataURL(fileobj);
			}
		});
	}
	return false;
}

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
	$control_event.val(app.toggle_date_format($control_event.val()));
	
	// set event
	$post_settings.find(".btn-set-event").on("click", function() {
		app.set_event($post, app.toggle_date_format($control_event.val()), $(this));
	});
	
	// tasks
	var $control_task = $post_settings.find(".control-task")
		.on("change", function() {
			app.convert_to_task($post, $(this).prop("checked"), $(this));
		});
	
	if($control_task.prop("checked")) {
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
	
		var $control_status = $post_settings.find(".control-status").on("change", function() {
			app.update_task_status($post, $(this).val(), $(this));
		});
	}
}

app.convert_to_task = function($post, checked, $control) {
	$control.prop("disabled", true);
	$.ajax({
		url: "/",
		type: "POST",
		data: {
			cmd: "aapkamanch.post.convert_to_task",
			post: $post.attr("data-name"),
			is_task: checked ? "1": "0"
		},
		statusCode: {
			403: function(xhr) {
				wn.msgprint("Not Permitted");
			},
			200: function(data) {
				$(".post-settings").remove();
				app.setup_post_settings($post, data.message);
				$post.find(".assigned-label").toggleClass("hide", !checked);
				$post.find(".assigned-label-fullname").html("");
			}
		}
	}).always(function() {
		$control.prop("disabled", false);
	})
	
}

app.assign_post = function($post, profile, $control) {
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
					$post.find(".assigned-label-fullname").html(fullname || "");
					if(app.get_unit()==="tasks" && !fullname) {
						$post.remove();
					}
				}
			}
		}
	}).always(function() {
		$control.val("").prop("disabled", false);
	});
};

app.set_event = function($post, event_datetime, $btn) {
	$btn.prop("disabled", true);
	$.ajax({
		url: "/",
		type: "POST",
		data: {
			cmd: "aapkamanch.post.set_event",
			post: $post.attr("data-name"),
			event_datetime: event_datetime
		},
		statusCode: {
			403: function(xhr) {
				wn.msgprint("Not Permitted");
			},
			200: function(data) {
				if(data.exc) {
					console.log(data.exc);
				} else {
					$(".post-settings").remove();
					app.setup_post_settings($post, data.message);
					$post.find(".event-label")
						.toggleClass("hide", !event_datetime)
						.find(".event-timestamp").attr("data-timestamp", event_datetime);
						app.format_event_timestamps();
				}
			}
		}
	}).always(function() {
		$btn.prop("disabled", false);
	});
};

app.update_task_status = function($post, status, $control) {
	$control.prop("disabled", true);
	$.ajax({
		url: "/",
		type: "POST",
		data: {
			cmd: "aapkamanch.post.update_task_status",
			post: $post.attr("data-name"),
			status: status
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
					app.setup_post_settings($post, data.message);
					$post.find(".assigned-label")
						.toggleClass("label-warning", status!=="Completed")
						.toggleClass("label-success", status==="Completed");
					if(app.get_unit()==="tasks" && status==="Completed") {
						$post.remove();
					}
				}
			}
		}
	}).always(function() {
		$control.val("").prop("disabled", false);
	});
};

app.format_event_timestamps = function() {
	$(".event-timestamp").each(function() {
		$(this).html(app.toggle_date_format($(this).attr("data-timestamp")));
	})
}

app.process_external_links = function(content) {
	return content.replace(/([^\(\[](ht|f)tp[s]?:\/\/[^\s\[\]\(\)]*)/g, '<a href="$1" target="_blank">$1</a>');
}