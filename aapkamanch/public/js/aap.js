var app = {};

// pages

// home
// states
// districts
// my groups
// login / signup
// profile

$(function() {
	app.setup_units();

	$(window).trigger("hashchange");
})

app.generators = {
	"unit": {
		render: function(page) { 
			var unit_name = app.get_route().split("/")[1];
			app.make_unit_page(page, unit_name); 
		},
	},
	"unit-list": {
		render: function(page) {
			var unit_name = app.get_route().split("/")[1];
			app.make_unit_list(page, unit_name);
		}
	}
}


app.setup_units = function() {
	app.unit_map = {"India":all_units};
	function walk_unit(unit) {
		$.each(unit.children || [], function(i, child_unit) {
			app.unit_map[child_unit.unit_name] = child_unit;
			walk_unit(child_unit);
		})
	}
	
	walk_unit(all_units);
}

app.make_unit_page = function(page, unit_name) {
	var unit = app.unit_map[unit_name];

	page
		.css({"padding":"15px"})
		.html('<div class="alert alert-warning">Feed will come here</div>');
	app.set_title(unit_name);
	if(unit.parent_unit)
		app.set_button("left", "unit-list/" + unit.parent_unit, unit.parent_unit);
	app.set_button("right", "unit-list/" + unit_name, unit.children_name);	
}

app.make_unit_list = function(page, unit_name) {
	var unit = app.unit_map[unit_name];
	
	var $list_group = $('<div class="list-group">').appendTo(page);

	$.each(unit.children, function(i, v) {
		$list = $('<a href="#unit/'+ v.unit_name+'" class="list-group-item">' + v.unit_name + 
			'<i class="icon-angle-right pull-right"></i></a>')
			.appendTo($list_group)
	});
	
	app.set_title(unit_name);
	app.set_button("left", "unit/" + unit.unit_name, unit.unit_name);
	app.set_button("right", null);
	
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

app.set_button = function(dir, route, title) {
	var $btn = $("."+dir+"-button");
	$btn.toggleClass("hide", !route);
	if(route) {
		$btn.find("a").attr("href", "#" + route);
		$("."+dir+"-title").html(title);
	} 
}

app.set_title = function(title) {
	$(".app-title").html(title);
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

