# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json
import os

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
	key = "permissions:{}".format(profile)
	permissions = cache.get_value(key) or {}
	if not permissions.get(unit):
		permissions[unit] = _get_access(unit, profile)
		cache.set_value(key, permissions)
		
	return permissions.get(unit)
	
def clear_permissions(profiles):
	if isinstance(profiles, basestring):
		profiles = [profiles]
	
	cache = webnotes.cache()
	for profile in profiles:
		cache.delete_value("permissions:{}".format(profile))
	
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
	return webnotes.conn.sql("""select name, name as url, unit_title, public_read, public_write, unit_type
		from tabUnit where 
		ifnull(`public_read`,0) = %s 
		and parent_unit=%s""", (public_read, unit), as_dict=1)
		
def get_task_count():
	return webnotes.conn.count("Post", {"assigned_to": webnotes.session.user})
	
def scrub_url(url):
	if not url or url.startswith("http"):
		return url
	return "/" + url
	
def get_icon(unit):
	icon_map = {
		"forum": "icon-comments",
		"events": "icon-calendar",
		"tasks": "icon-pencil"
	}
	unit_type = unit["unit_type"].lower()
	icon = icon_map.get(unit_type) or ""
	color_class = ""
	if not unit.get("public_read"):
		color_class = "text-warning"
	
	return '<i class="icon-fixed-width {} {}"></i>'.format(icon, color_class)

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
	if not hasattr(webnotes.local, "unit_views"):
		with open(os.path.join(os.path.dirname(__file__), "unit_views.json"), "r") as unit_views:
			webnotes.local.unit_views = json.loads(unit_views.read())
	
	if isinstance(unit, basestring):
		unit = webnotes.doc("Unit", unit)
		
	views = webnotes.local.unit_views.get(unit.unit_type, {}).copy()

	for view, opts in views.items():
		if opts.get("url"):
			opts["url"] = opts["url"].format(unit=unit.name, post=None)
	
	return views

def clear_cache():
	"""clear all caches related to aapkamanch"""
	# unit caches
	import unit
	from .post import clear_post_cache
	
	for name in webnotes.conn.sql_list("""select name from `tabUnit`"""):
		unit.clear_unit_views(name)
		
	# unit access for profiles
	clear_permissions(webnotes.conn.sql_list("""select name from `tabProfile`"""))
	
	# post pages
	for name in webnotes.conn.sql_list("""select name from `tabPost` where ifnull(parent_post, '')=''"""):
		clear_post_cache(name)
	