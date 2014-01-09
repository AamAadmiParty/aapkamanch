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
			"fb_education": data.get("education") and data.get("education")[-1].get("type")
		})
		profile.ignore_permissions = True
		profile.insert()
	
	webnotes.local.login_manager.user = user
	webnotes.local.login_manager.post_login()

	return get_user_details(data["unit"])

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
	
	access = None
	
	if unit != "tasks":
		access = get_access(unit)

	out = {
		"access": access,
		"fb_username": get_fb_username(),
		"task_count": get_task_count()
	}
	
	if access and access.get("read"):
		out["private_units"] = webnotes.get_template("templates/includes/unit_list.html")\
			.render({"children":get_child_unit_items(unit, public=0)})

	return out

@webnotes.whitelist()
def get_access(unit, profile=None):
	# TODO: memcache this
	
	if not profile:
		profile = webnotes.session.user
	
	lft, rgt = webnotes.conn.get_value("Unit", unit, ["lft", "rgt"])
	
	if not (lft and rgt):
		raise webnotes.ValidationError("Please rebuild Unit Tree")
	
	read = write = admin = 0
	
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


def get_fb_username():
	return webnotes.cache().get_value(webnotes.session.user + ":fb_username", 
		lambda: webnotes.conn.get_value("Profile", webnotes.session.user, "fb_username"))

def get_fb_userid(fb_access_token):
	import requests
	response = requests.get("https://graph.facebook.com/me?access_token=" + fb_access_token)
	if response.status_code==200:
		return response.json().get("id")
	else:
		return webnotes.AuthenticationError
		
def is_public(unit):
	return webnotes.cache().get_value("is_public:" + unit, lambda: webnotes.conn.get_value("Unit", unit, "public"))
	
def get_child_unit_items(unit, public):
	return webnotes.conn.sql("""select name, name as url, unit_title, public, unit_type
		from tabUnit where 
		ifnull(`public`,0) = %s 
		and parent_unit=%s""", (public, unit), as_dict=1)
		
def get_task_count():
	return webnotes.conn.count("Post", {"assigned_to": webnotes.session.user})