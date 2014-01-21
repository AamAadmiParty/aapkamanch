# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

@webnotes.whitelist(allow_guest=True)
def add_user(data):
	data = json.loads(data)
	
	if not (data.get("id") and data.get("fb_access_token")):
		raise webnotes.ValidationError

	user = data["email"]
		
	if not get_fb_userid(data.get("fb_access_token")):
		# garbage
		raise webnotes.ValidationError
	
	if not webnotes.conn.exists("Profile", user):
		if data.get("birthday"):
			b = data.get("birthday").split("/")
			data["birthday"] = b[2] + "-" + b[0] + "-" + b[1]
		
		profile = webnotes.bean({
			"doctype":"Profile",
			"first_name": data["first_name"],
			"last_name": data["last_name"],
			"email": data["email"],
			"enabled": 1,
			"new_password": webnotes.generate_hash(data["email"]),
			"fb_username": data["username"],
			"fb_userid": data["id"],
			"fb_location": data.get("location", {}).get("name"),
			"fb_hometown": data.get("hometown", {}).get("name"),
			"fb_age_range": data.get("age_range") and "{min}-{max}".format(**data.get("age_range")),
			"birth_date":  data.get("birthday"),
			"fb_bio": data.get("bio"),
			"fb_education": data.get("education") and data.get("education")[-1].get("type"),
			"user_type": "Website User"
		})
		profile.ignore_permissions = True
		profile.get_controller().no_welcome_mail = True
		profile.insert()
	
	webnotes.local.login_manager.user = user
	webnotes.local.login_manager.post_login()

@webnotes.whitelist(allow_guest=True)
def get_user_details(unit, fb_access_token=None):
	if fb_access_token:
		fb_userid = get_fb_userid(fb_access_token)
		profile = webnotes.conn.get_value("Profile", {"fb_userid": fb_userid})
		
		if not profile:
			raise webnotes.AuthenticationError
		
		# login
		webnotes.local.login_manager.user = profile
		webnotes.local.login_manager.post_login()
	
	out = {
		"user_image": get_user_image(),
		"task_count": get_task_count()
	}
	
	access = None
	if unit != "tasks":
		access = get_access(unit)
		
	out["access"] = access
	
	if access and access.get("read"):
		out["private_units"] = webnotes.get_template("templates/includes/unit_list.html")\
			.render({"children": get_child_unit_items(unit, public_read=0)})
	
	return out

@webnotes.whitelist()
def get_access(unit, profile=None):
	if not profile:
		profile = webnotes.session.user
	
	unit = unit.lower()
	cache = webnotes.cache()
	key = "unit_access:{}".format(profile)
	unit_access = cache.get_value(key) or {}
	if not unit_access.get(unit):
		unit_access[unit] = _get_access(unit, profile)
		cache.set_value(key, unit_access)
		
	return unit_access.get(unit)
	
def clear_unit_access(profiles):
	if isinstance(profiles, basestring):
		profiles = [profiles]
	
	cache = webnotes.cache()
	for profile in profiles:
		cache.delete_value("unit_access:{}".format(profile))
	
def _get_access(unit, profile):
	lft, rgt, public_read, public_write = webnotes.conn.get_value("Unit", unit, 
		["lft", "rgt", "public_read", "public_write"])

	if not (lft and rgt):
		raise webnotes.ValidationError("Please rebuild Unit Tree")
		
	read = write = admin = 0

	if public_write:
		read = write = 1

	# give read access for public_read pages
	elif public_read:
		read = 1

	if profile != "Guest":
		for perm in webnotes.conn.sql("""select 
			up.`read`, up.`write`, up.`admin`, u.lft, u.rgt, u.name
			from `tabUnit Profile` up, tabUnit u
			where up.profile = %s
				and up.parent = u.name order by lft asc""", (profile,), as_dict=True):
			if perm.lft <= lft and perm.rgt >= rgt:
				if not read: read = perm.read
				if not write: write = perm.write
				if not admin: admin = perm.admin
				if write: read = write
		
				if read and write and admin:
					break

	return {
		"read": read,
		"write": write,
		"admin": admin
	}

def get_user_image():
	return webnotes.cache().get_value(webnotes.session.user + ":user_image", 
		lambda: webnotes.conn.get_value("Profile", webnotes.session.user, "user_image"))

def get_fb_userid(fb_access_token):
	import requests
	response = requests.get("https://graph.facebook.com/me?access_token=" + fb_access_token)
	if response.status_code==200:
		return response.json().get("id")
	else:
		return webnotes.AuthenticationError
		
def get_child_unit_items(unit, public_read):
	return webnotes.conn.sql("""select name, name as url, unit_title, public_read, unit_type
		from tabUnit where 
		ifnull(`public_read`,0) = %s 
		and parent_unit=%s""", (public_read, unit), as_dict=1)
		
def get_task_count():
	return webnotes.conn.count("Post", {"assigned_to": webnotes.session.user})
	
def scrub_url(url):
	if not url or url.startswith("http"):
		return url
	return "/" + url
	
def get_icon(key):
	return
	# icon_map = {
	# 	"forum": "icon-comments",
	# 	"private": "icon-lock",
	# 	"public_write": "icon-group",
	# 	"events": "icon-calendar",
	# 	"tasks": "icon-pencil",
	# 	"questions": "icon-question",
	# }
	# key = key.lower()
	# return '<i class="{}"></i>'.format(icon_map.get(key)) if icon_map.get(key) else ""

def update_gravatar(bean, trigger):
	import md5
	if not bean.doc.user_image:
		if bean.doc.fb_username:
			bean.doc.user_image = "https://graph.facebook.com/" + bean.doc.fb_username + "/picture"
		else:
			bean.doc.user_image = "https://secure.gravatar.com/avatar/" + md5.md5(bean.doc.name).hexdigest() \
				+ "?d=retro"
				
		webnotes.cache().delete_value(bean.doc.name + ":user_image")
		
	webnotes.cache().delete_value("total_users")
		
def update_website_context(context):
	context.update({
		"total_users": webnotes.cache().get_value("total_users", 
			lambda: str(webnotes.conn.sql("""select count(*) from tabProfile""")[0][0]))
	})
	
def get_views(unit):
	if isinstance(unit, basestring):
		unit = webnotes.doc("Unit", unit)
	
	unit_views = {
		"Forum": [
			{"view": "popular", "url": "/{}".format(unit.name), "label": "Popular", "icon": "icon-heart", 
				"default": True, "upvote": True},
			{"view": "feed", "url": "/{}/{}".format(unit.name, "feed"), "label": "Feed", "icon": "icon-rss", 
				"upvote": True},
			{"view": "add", "url": "/{}/{}".format(unit.name, "add"), "label": "Add Post", "icon": "icon-plus",
				"class": "hide"},
			{"view": "edit", "url": "/{}/{}".format(unit.name, "edit"), "label": "Edit Post", "icon": "icon-pencil",
				"class": "hide", "no_cache": True},
			{"view": "settings", "url": "/{}/{}".format(unit.name, "settings"), "label": "Settings", "icon": "icon-cog",
				"class": "hide"},
			{"view": "post", "url": "/{}/{}".format(unit.name, "post"), "label": "Post", "icon": "icon-comments",
				"class": "hide"},
		],
		"Tasks": [
			{"view": "open", "url": "/{}".format(unit.name), "label": "Open", "icon": "icon-inbox", 
				"default": True, "upvote": True},
			{"view": "closed", "url": "/{}/{}".format(unit.name, "closed"), "label": "Closed", "icon": "icon-smile"},
			{"view": "add", "url": "/{}/{}".format(unit.name, "add"), "label": "Add Task", "icon": "icon-plus",
				"class": "hide"},
			{"view": "edit", "url": "/{}/{}".format(unit.name, "edit"), "label": "Edit Task", "icon": "icon-pencil",
				"class": "hide", "no_cache": True},
			{"view": "settings", "url": "/{}/{}".format(unit.name, "settings"), "label": "Settings", "icon": "icon-cog",
				"class": "hide"},
			{"view": "post", "url": "/{}/{}".format(unit.name, "post"), "label": "Post", "icon": "icon-comments",
				"class": "hide"},
		],
		"Events": [
			{"view": "upcoming", "url": "/{}".format(unit.name), "label": "Upcoming", "icon": "icon-calendar", 
				"default": True},
			{"view": "past", "url": "/{}/{}".format(unit.name, "past"), "label": "Past", "icon": "icon-time"},
			{"view": "add", "url": "/{}/{}".format(unit.name, "add"), "label": "Add Event", "icon": "icon-plus",
				"class": "hide"},
			{"view": "edit", "url": "/{}/{}".format(unit.name, "edit"), "label": "Edit Event", "icon": "icon-pencil",
				"class": "hide", "no_cache": True},
			{"view": "settings", "url": "/{}/{}".format(unit.name, "settings"), "label": "Settings", "icon": "icon-cog",
				"class": "hide"},
			{"view": "post", "url": "/{}/{}".format(unit.name, "post"), "label": "Post", "icon": "icon-comments",
				"class": "hide"},
		]
	}
	
	return unit_views.get(unit.unit_type) or []
	
def get_view_options(unit, view):
	for opts in get_views(unit):
		if opts["view"] == view:
			return opts
	return {}