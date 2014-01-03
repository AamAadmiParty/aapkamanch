var aap = {};


$(function() {
	$(window).trigger("hashchange");

	$(".left-button").click(function() {
		aap.page.parent && aap.set_route(aap.page.parent);
	})
})

aap.routes = {
	"home": function() { aap.show_list(aap.pages.home); },
	"states": function() { aap.show_list(aap.pages.states); },
}

aap.set_route = function(route) {
	window.location.hash = route;
}

$(window).on("hashchange", function() {
	var route = aap.get_route();

	if(aap.routes[route]) {
		aap.routes[route]();
	} else {
		aap.route["not-found"]();
	}
})

aap.get_route = function() {
	var route = window.location.hash;
	if(route.substr(0,1)=='#') 
		route = route.substr(1);
	if(!route) 
		route = "home";
	return route;
}

aap.pages = {}

aap.pages.home = {
	items: [
		{ "label": "My Groups" },	
		{ "label": "All Groups", "click": function() { aap.set_route("states") } },	
		{ "label": "Profile" },	
	]
}

aap.pages.states = {
	parent: "home",
	items: [
		{ label: "Delhi" },
		{ label: "Maharashtra" },
	]
};

aap.show_list = function(page) {
	
	var $list_group = $('<div class="list-group">').appendTo($("#content").empty());

	$.each(page.items, function(i, v) {
		$list = $('<a class="list-group-item">' + v.label + 
			'<i class="icon-angle-right pull-right"></i></a>')
			.appendTo($list_group)
			.click(v.click);
	});
	
	$(".left-button")
		.toggleClass("hide", !page.parent);
		
	aap.page = page;
}

