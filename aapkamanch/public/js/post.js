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
	} else if($('.post-editor [data-fieldname="event_datetime"]').length && !values.event_datetime) {
		wn.msgprint("Please enter Event's Date and Time!");
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
	var values = app.get_editor_values();
	if(!values) {
		return;
	}

	$(btn).prop("disabled", true);
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
};

app.setup_event_editor = function() {
	var $post_editor = $(".post-editor");
	var $control_event = $post_editor.find('.control-event').empty();
	var $event_field = $post_editor.find('[data-fieldname="event_datetime"]');

	var set_event = function($control) {
		var datetime = app.datetimepicker.obj_to_str($control_event.datepicker("getDate"));
		if($event_field.val() !== datetime) {
			$event_field.val(datetime);
		}
	};

	app.setup_datepicker({
		$control: $control_event,
		onClose: function() { set_event($control_event) }
	});

	if($event_field.val()) {
		$control_event.val(app.datetimepicker.format_datetime($event_field.val()));
	}
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