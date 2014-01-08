// AAP Ka Manch, License GNU General Public License v3

$(function() {
	$(".btn-settings").on("click", app.toggle_unit_settings);
})

app.toggle_unit_settings = function() {
	if(app.settings_shown) {
		$(".permission-editor-area").toggle(false);
		app.settings_shown = false;
	} else {
		if(!app.settings_loaded) {
			$.ajax({
				url:"/",
				data: {
					cmd: "aapkamanch.permissions.get_permission_html",
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
					$(".permission-editor-area").on("click", "[type='checkbox']", app.update_permission)
				}
			})
		} else {
			$(".permission-editor-area").toggle(true);
		}
		app.settings_shown = true;
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
