var app = {};

// pages

// home
// states
// districts
// my groups
// login / signup
// profile

$(function() {
	$(".left-button").click(function() {
		var parent = app.page.attr("data-parent");
		parent && app.set_route(parent);
	})

	app.setup_states();

	$(window).trigger("hashchange");
})

app.generators = {
	"home": {
		render: function(page) { 
			app.make_list_page(page, app.lists.home); }
	},
	"states": {
		render: function(page) { 
			app.make_list_page(page, app.lists.states);
			page.attr("data-parent", "home");
		},
	},
	"state": {
		render: function(page) { 
			var state = app.get_route().split("/")[1];
			app.make_list_page(page, app.lists[state]); 
			page.attr("data-parent", "states");
		},
	},
}

app.lists = {}
app.lists.home = {
	title: "AAP Ka Manch",
	items: [
		{ "label": "My Groups" },	
		{ "label": "All Groups", "route": "states" },	
		{ "label": "Profile" },	
	]
}


app.setup_states = function() {
	var states = Object.keys(all_states);
	app.lists.states = {
		title: "States",
		parent: "home",
		items: []
	};
	$.each(states.sort(), function(i, state) {
		app.lists.states.items.push({label:state, route:"state/" + state});
		app.lists[state] = {
			title: state,
			parent: "states",
			items: []
		}
		$.each(all_states[state].sort(), function(i, district) {
			app.lists[state].items.push({label: district, route:"groups/" + district});
		})
	});
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
		parent_title = app.pages[parent].attr("title");
		$(".parent-title")
			.html(app.pages[parent].attr("title"));
		$(".left-button").toggleClass("hide", false);
	} else {
		$(".left-button").toggleClass("hide", true);
	}
}

app.get_route = function() {
	var route = window.location.hash;
	if(route.substr(0,1)=='#') 
		route = route.substr(1);
	if(!route) 
		route = "home";
	return route;
}

// lists

app.make_list_page = function(page, list) {
	
	var $list_group = $('<div class="list-group">').appendTo(page);

	$.each(list.items, function(i, v) {
		$list = $('<a class="list-group-item">' + v.label + 
			'<i class="icon-angle-right pull-right"></i></a>')
			.appendTo($list_group)
			.click(function() { 
				if(v.click) {
					v.click();
				} else if(v.route) {
					app.set_route(v.route);
				}
			});
	});
	
	page.attr("title", list.title);
	return page;
}

