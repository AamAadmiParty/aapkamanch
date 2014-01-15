// AAP Ka Manch, License GNU General Public License v3

$(function() {
	if(window.app.view=="settings") {
		app.setup_unit_settings();
	}
});

app.setup_unit_settings = function() {	
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
	$(".btn-settings").parent().addClass("active");
	
	// disabled forum if not public
	var control_public = $(".control-add-group-public").click(function() {
		if(!$(this).prop("checked")) {
			$(".control-add-group-forum").prop("checked", false).prop("disabled", true);
		} else {
			$(".control-add-group-forum").prop("disabled", false);
		}
	}).trigger("click").trigger("click"); // hack
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
				public: $(".control-add-group-public").is(":checked") ? 1 : 0,
				forum: $(".control-add-group-forum").is(":checked") ? 1 : 0
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
