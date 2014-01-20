// AAP Ka Manch, License GNU General Public License v3

app.get_editor_values = function() {
	var values = {};
	$.each($('.post-editor [data-fieldname]'), function(i, ele) {
		var $ele = $(ele);
		values[$ele.attr("data-fieldname")] = $ele.val();
	});
	
	values.parent_post = $(".post-editor").attr("data-parent-post");
	values.picture_name = $(".control-post-add-picture").val();

	var dataurl = $(".post-picture img").attr("src");
	values.picture = dataurl ? dataurl.split(",")[1] : ""
	
	// validations
	if(!values.title) {
		wn.msgprint("Please enter title!");
		return;
	} else if(!values.content) {
		wn.msgprint("Please enter some text!");
		return;
	}
	
	// post process
	// convert links in content
	values.content = app.process_external_links(values.content);
	
	return values;
}

app.bind_add_post = function() {
	$(".btn-post-add").on("click", app.add_post);

	$pic_input = $(".control-post-add-picture").on("change", app.add_picture);
	$(".btn-post-add-picture").on("click", function() { 
		$pic_input.click();
	});
}

app.bind_save_post = function() {
	$(".btn-post-add").addClass("hide")
	$(".btn-post-save").removeClass("hide").on("click", app.save_post);
}

app.add_post = function() {
	if(window.app.post) {
		wn.msgprint("Post already exists. Cannot add again!");
		return;
	}
	
	app._update_post(this, "aapkamanch.post.add_post")
};

app.save_post = function() {
	if(!window.app.post) {
		wn.msgprint("Post does not exist. Please add post!");
		return;
	}
	
	app._update_post(this, "aapkamanch.post.save_post");
}

app._update_post = function(btn, cmd) {
	$(btn).prop("disabled", true);
	var values = app.get_editor_values();
	$.ajax({
		type: "POST",
		url: "/",
		data: $.extend({
			cmd: cmd,
			unit: app.get_unit(),
			post: window.app.post || undefined
		}, values),
		success: function(data) {
			if(data.exc){
				console.log(data.exc);
			} else if(values.parent_post) {
				window.location.href = "/post/" + values.parent_post;
			} else {
				window.location.href = "/" + app.get_unit().toLowerCase();
			}
		}
	}).always(function() {
		$(btn).prop("disabled", false);
	});
}

app.add_picture = function() {
	if (this.type === 'file' && this.files && this.files.length > 0) {
		$.each(this.files, function (idx, fileobj) {
			if (/^image\//.test(fileobj.type)) {
				$.canvasResize(fileobj, {
					width: 500,
					height: 0,
					crop: false,
					quality: 80,
					callback: function(data, width, height) {
						$(".post-picture").toggle(true).find("img").attr("src", data);
					}
				});
			}
		});
	}
	return false;
}

app.setup_tasks_editor = function() {
	// assign events
	var $post_editor = $(".post-editor");
	var $control_assign = $post_editor.find('.control-assign');
	
	var bind_close = function() {
		var close = $post_editor.find("a.close")
		if(close.length) {
			close.on("click", function() {
				// clear assignment
				$post_editor.find(".assigned-to").addClass("hide");
				$post_editor.find(".assigned-profile").html("");
				$post_editor.find('[data-fieldname="assigned_to"]').val(null);
				$control_assign.val(null);
			});
		}
	}
	
	if($control_assign.length) {
		app.setup_autosuggest({
			$control: $control_assign,
			select: function(value, item) {
				var $assigned_to = $post_editor.find(".assigned-to").removeClass("hide");
				$assigned_to.find(".assigned-profile").html(item.profile_html);
				$post_editor.find('[data-fieldname="assigned_to"]').val(value);
				bind_close();
			},
			method: "aapkamanch.post.suggest_user"
		});
		bind_close();
	}
}

app.setup_post_settings = function($post, post_settings_html) {
	var $post_settings = $(post_settings_html).appendTo($post.find(".post-settings-area"));
	
	var $control_event_check = $post_settings.find(".control-event-check").on("change", function() {
		app.convert_to_event($post, $(this).prop("checked"), $(this));
	});
	
	if($control_event_check.prop("checked")) {
		var $control_event = $post_settings.find(".control-event").empty();
	
		var set_event = function($control) {
			var datetime = app.datetimepicker.obj_to_str($control_event.datepicker("getDate"));
			if($control_event.attr("data-event_datetime") !== datetime) {
				app.set_event($post, datetime, $control);
			}
		};
	
		app.setup_datepicker({
			$control: $control_event,
			onClose: function() { set_event($control_event) }
		});
	
		if($control_event.attr("data-event_datetime")) {
			$control_event.val(app.datetimepicker.format_datetime($control_event.attr("data-event_datetime")));
		}
	}
	
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
						.find(".event-timestamp").attr("data-timestamp", event_datetime);
						app.format_event_timestamps();
				}
			}
		}
	}).always(function() {
		$btn.prop("disabled", false);
	});
};

app.format_event_timestamps = function() {
	var format = function(datetime) {
		if(!datetime) return "";
		var date = datetime.split(" ")[0].split("-");
		var time = datetime.split(" ")[1].split(":");
		var tt = "am";
		if(time[0] >= 12) {
			time[0] -= 12;
			tt = "pm";
		} else if(time[0] == "00") {
			time[0] = 12;
		}
		var hhmm = [time[0], time[1]].join(":")
		
		return [date[2], date[1], date[0]].join("-") + " " + hhmm + " " + tt;
	}
	$(".event-timestamp").each(function() {
		$(this).html(format($(this).attr("data-timestamp")));
	})
}

app.process_external_links = function(content) {
	return content.replace(/([^\(\[](ht|f)tp[s]?:\/\/[^\s\[\]\(\)]*)/g, function(match, p1) {
		// hack to add back surrounding whitespace
		var old_p1 = p1;
		p1 = p1.trim();
		var processed = "["+p1+"]("+p1+")";
		if(old_p1!=p1) {
			processed = old_p1.replace(p1, "") + processed;
		}
		return processed;
	});
}

app.filter_posts_by_status = function(status) {
	$.ajax({
		url: "/",
		data: {
			"cmd": "aapkamanch.post.get_post_list_html",
			"unit": app.get_unit(),
			"view": app.get_view(),
			"status": status
		},
		statusCode: {
			200: function(data) {
				if(data.exc) {
					console.log(data.exc);
				} else {
					$(".post-list").empty()
						.html(data.message)
					
					if(status) {
						var alert = $('<div class="alert alert-warning">\
								Showing Tasks with status: ' + status + 
								' <a class="pull-right close">&times;</a> \
							</div>')
							.css("margin-top", "7px")
							.prependTo($(".post-list"))
							.find("a").on("click", function() {
								window.location.hash = "";
							});
					}
						
					app.format_event_timestamps();
					wn.datetime.refresh_when();
				}
			}
		}
	})
}