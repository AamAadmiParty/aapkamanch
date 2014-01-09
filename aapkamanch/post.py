# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from webnotes.utils import get_fullname
from helpers import get_access
from webnotes.utils.file_manager import get_file_url, save_file

@webnotes.whitelist()
def get_post_list_html(unit, limit_start=0, limit_length=20):
	access = get_access(unit)
	if webnotes.local.form_dict.cmd=="get_post_list_html":
		# for paging
		if not access.get("read"):
			raise webnotes.PermissionError
	
	posts = webnotes.conn.sql("""select p.name, p.unit,
		p.assigned_to, p.event_datetime, p.assigned_to_fullname, p.picture_url,
		p.creation, p.content, pr.fb_username, pr.first_name, pr.last_name 
		from tabPost p, tabProfile pr
		where p.unit=%s and pr.name = p.owner order by p.creation desc limit %s, %s""", 
			(unit, limit_start, limit_length), as_dict=True)
			
	return webnotes.get_template("templates/includes/post_list.html").render({"posts": posts, 
		"limit_start":limit_start, "write": access.get("write")})

@webnotes.whitelist()
def add_post(unit, content, picture, picture_name):
	access = get_access(unit)
	if not access.get("write"):
		raise webnotes.PermissionError
			
	post = webnotes.bean({
		"doctype":"Post",
		"content": content,
		"unit": unit
	})
	post.ignore_permissions = True
	post.insert()

	if picture_name and picture:
		file_data = save_file(picture_name, picture, "Post", post.doc.name, decode=True)
		post.doc.picture_url = file_data.file_name or file_data.file_url
		webnotes.conn.set_value("Post", post.doc.name, "picture_url", post.doc.picture_url)
	
	post.doc.fields.update(webnotes.conn.get_value("Profile", webnotes.session.user, 
		["first_name", "last_name", "fb_username"], as_dict=True))
	
	webnotes.cache().delete_value("unit_html:" + unit)
	
	return webnotes.get_template("templates/includes/post.html").render({"post":post.doc.fields,
		"write": access.get("write")})

@webnotes.whitelist()
def get_post_settings(unit, post_name):
	if not get_access(unit).get("write"):
		raise webnotes.PermissionError
	
	post = webnotes.bean("Post", post_name).doc
	if post.unit != unit:
		raise webnotes.ValidationError("Post does not belong to unit.")
	
	profile = None
	if post.assigned_to:
		profile = webnotes.conn.get_value("Profile", post.assigned_to, 
			["first_name", "last_name", "fb_username", "fb_location", "fb_hometown"], as_dict=True)
		
	return webnotes.get_template("templates/includes/post_settings.html").render({
		"post": post,
		"unit_profile": profile
	})
	
@webnotes.whitelist()
def assign_post(post, profile=None):
	post = webnotes.bean("Post", post)

	if not get_access(post.doc.unit).get("write"):
		raise webnotes.PermissionError("You are not allowed edit this post")
	
	if profile and not get_access(post.doc.unit, profile).get("write"):
		raise webnotes.PermissionError("Selected user does not have 'write' access to this post")
		
	if profile and post.doc.assigned_to:
		webnotes.throw("Someone is already assigned to this post. Please refresh.")
	
	post.doc.assigned_to = profile
	post.doc.assigned_to_fullname = get_fullname(profile) if profile else None
	post.ignore_permissions = True
	post.save()
	
	return {
		"post_settings_html": get_post_settings(post.doc.unit, post.doc.name),
		"assigned_to_fullname": post.doc.assigned_to_fullname
	}

@webnotes.whitelist()
def set_event(post, event_datetime):
	post = webnotes.bean("Post", post)

	if not get_access(post.doc.unit).get("write"):
		raise webnotes.PermissionError("You are not allowed edit this post")
		
	post.doc.event_datetime = event_datetime
	post.ignore_permissions = True
	post.save()
	
	return get_post_settings(post.doc.unit, post.doc.name)

@webnotes.whitelist()
def suggest_user(unit, term):
	"""suggest a user that has read permission in this unit tree"""
	profiles = webnotes.conn.sql("""select 
		pr.name, pr.first_name, pr.last_name, 
		pr.fb_username, pr.fb_location, pr.fb_hometown
		from `tabProfile` pr
		where (pr.first_name like %(term)s or pr.last_name like %(term)s)
		and pr.fb_username is not null""", 
		{"term": "%{}%".format(term), "unit": unit}, as_dict=True)
	
	template = webnotes.get_template("templates/includes/profile_display.html")
	return [{"value": pr.name, "profile_html": template.render({"unit_profile": pr})}
		for pr in profiles]
	