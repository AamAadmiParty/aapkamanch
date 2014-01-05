var app = {};

// pages

// home
// states
// districts
// my groups
// login / signup
// profile

$(function() {
	$(window).trigger("hashchange");
})

app.generators = {
	"unit": {
		render: function(page) { 
			var unit_name = app.get_route().split("/")[1];
			app.make_unit_page(page, unit_name); 
		},
	},
}


// app.setup_units = function() {
// 	app.unit_map = {"India":all_units};
// 	function walk_unit(unit) {
// 		$.each(unit.children || [], function(i, child_unit) {
// 			app.unit_map[child_unit.unit_name] = child_unit;
// 			walk_unit(child_unit);
// 		})
// 	}
// 	
// 	walk_unit(all_units);
// }

app.make_unit_page = function(page, unit_name) {
	$.ajax({
		url: "/",
		data: {
			cmd: "aapkamanch.helpers.get_parent_and_children",
			unit_name: unit_name
		},
		dataType:"json",
		success: function(data) {
			data = data.message;
			var $list_group = $('<div class="list-group"></div>').appendTo(page);
			var $feed = $('<div class="feed-list">\
					<div class="alert alert-warning">Feed comes here.</div>\
				</div>').appendTo(page);

			$.each(data.children, function(i, v) {
				$list = $('<a href="#unit/'+ v+'" class="list-group-item">' + v + 
					'<i class="icon-angle-right pull-right"></i></a>')
					.appendTo($list_group)
			});
	
			var titlebar = {
				"title": unit_name,
				"page": page
			}
			if(data.parent) {
				titlebar.left = {title:data.parent, route: "unit/"+data.parent};
			}
			app.set_titlebar(titlebar);
		}
	})
	
	return page;
}


// utils

// route
$(window).on("hashchange", function() {
	var route = app.get_route();

	if(app.pages[route]) {
		app.show_page(route);
	} else {
		var page = app.add_page(route);
		var parts = route.split('/');
		if(app.generators[parts[0]]) {
			app.generators[parts[0]].render(page);
			app.show_page(route);
		} else {
			app.route["not-found"]();
		}
	}
})

app.set_route = function(route) {
	window.location.hash = route;
}

// app.set_button = function(dir, route, title) {
// 	var $btn = $("."+dir+"-button");
// 	$btn.toggleClass("hide", !route);
// 	if(route) {
// 		$btn.find("a").attr("href", "#" + route);
// 		$("."+dir+"-title").html(title);
// 	} 
// }
// 
// app.set_title = function(title) {
// 	$(".app-title").html(title);
// }

app.set_titlebar = function(opts) {
	var left="", right="", title="";
	if(opts.left) {
		left = '<div class="left-button topnav-button">\
			<a href="#'+opts.left.route+'">\
				<i class="icon-angle-left"></i> \
				<span class="left-title">'+opts.left.title+'</span></a>\
		</div>';
	}
	if(opts.right) {
		right = '<div class="right-button topnav-button text-right">\
			<a href="#'+opts.right.route+'">\
				<span class="right-title">'+opts.right.title+'</span> \
					<i class="icon-angle-right"></i></a>\
		</div>'
	}

	$('<div class="titlebar">\
		<div class="row" style="padding: 10px">\
			<div class="col-xs-4">'+left+'</div>\
			<div class="col-xs-4 text-center"><b class="app-title">'+opts.title+'</b></div>\
			<div class="col-xs-4">'+right+'</div>\
		</div>\
		<div class="row" style="padding-left: 15px; padding-right: 15px;">\
			<div class="col-xs-6" style="background-color: #F28300; height: 6px;"></div>\
			<div class="col-xs-6" style="background-color: #61a220; height: 6px;"></div>\
		</div>\
	</div>').prependTo(opts.page);
}

app.pages = {};

app.add_page = function(route) {
	app.pages[route] = $('<div class="page"></div>')
		.toggle(false)
		.appendTo("#content");
	return app.pages[route];
}

app.show_page = function(route) {
	if(app.page) 
		app.page.toggle(false);
	app.page = app.pages[route];
	app.page.toggle(true);
	$(".app-title").html(app.page.attr("title"));
	parent = app.page.attr("data-parent");
	if(parent) {
		if(!app.pages[parent] && app.generators[parent]) {
			// render parent page too
			app.generators[parent].render(app.add_page(parent));
		}
	}
}

app.get_route = function() {
	var route = window.location.hash;
	if(route.substr(0,1)=='#') 
		route = route.substr(1);
	if(!route) 
		route = "unit/India";
	return route;
}

