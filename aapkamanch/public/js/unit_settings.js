// AAP Ka Manch, License GNU General Public License v3

$(function() {
	$(".btn-settings").on("click", app.toggle_unit_settings);
})

app.toggle_unit_settings = function() {
	if(app.settings_shown) {
		$(".permission-editor-area").toggle(false);
		$(".btn-settings").removeClass("btn-primary").addClass("btn-default");
		app.settings_shown = false;
	} else {
		if(!app.settings_loaded) {
			$.ajax({
				url:"/",
				data: {
					cmd: "aapkamanch.permissions.get_unit_settings_html",
					unit: app.get_unit()
				},
				success: function(data) {
					if(data.exc) 
						console.log(data.exc)
					$(".permission-editor-area").toggle(true)
						.empty().html(data.message);
					app.settings_loaded = true;
					
					// autosuggest
					app.setup_autosuggest({
						$control: $(".add-user-control"),
						select: function(value) { 
							app.add_unit_profile(value); 
						},
						method: "aapkamanch.permissions.suggest_user"
					});

					
					// trigger for change permission
					$(".permission-editor-area").on("click", ".unit-profile [type='checkbox']", 
						app.update_permission);
					$(".permission-editor-area").find(".btn-add-group").on("click", app.add_group);
					$(".btn-settings").removeClass("btn-default").addClass("btn-primary");				}
			})
		} else {
			$(".permission-editor-area").toggle(true);
			$(".btn-settings").removeClass("btn-default").addClass("btn-primary");
		}
		app.settings_shown = true;
	}
}

app.add_group = function() {
	var $control = $(".control-add-group"),
		$btn = $(".btn-add-group");
	if($control.val()) {
		$btn.prop("disabled", true);
		$.ajax({
			url:"/",
			type:"POST",
			data: {
				cmd:"aapkamanch.unit.add_unit",
				unit: app.get_unit(),
				new_unit: $control.val(),
				public: $(".control-add-group-public").is(":checked") ? 1 : 0
			},
			statusCode: {
				403: function() {
					wn.msgprint("Name Not Permitted");
				},
				200: function(data) {
					if(data.exc) {
						console.log(data.exc);
						if(data._server_messages) wn.msgprint(data._server_messages);
					} else {
						wn.msgprint("Group Added, refreshing...");
						setTimeout(function() { window.location.reload(); }, 1000)
					}
				}
			}
		}).always(function() {
			$btn.prop("disabled",false);
			$control.val("");
		})
	}
}

app.update_permission = function() {
	var $chk = $(this);
	var $tr = $chk.parents("tr:first");
	$chk.prop("disabled", true);
	
	$.ajax({
		url: "/",
		type: "POST",
		data: {
			cmd: "aapkamanch.permissions.update_permission",
			profile: $tr.attr("data-profile"),
			perm: $chk.attr("data-perm"),
			value: $chk.prop("checked") ? "1" : "0",
			unit: app.get_unit()
		},
		statusCode: {
			403: function() {
				wn.msgprint("Not Allowed");
			},
			200: function(data) {
				$chk.prop("disabled", false);
				if(data.exc) {
					$chk.prop("checked", !$chk.prop("checked"));
					console.log(data.exc);
				} else {
					if(!$tr.find(":checked").length) $tr.remove();
				}
			}
		},
	});
}

app.add_unit_profile = function(profile) {
	$.ajax({
		url: "/",
		type: "POST",
		data: {
			cmd: "aapkamanch.permissions.add_unit_profile",
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
