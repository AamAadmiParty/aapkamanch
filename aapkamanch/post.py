# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json
import markdown2

from webnotes.utils import get_fullname, cint
from helpers import get_access
from .aapkamanch.doctype.unit.unit import clear_unit_views
from webnotes.utils.file_manager import get_file_url, save_file

@webnotes.whitelist(allow_guest=True)
def add_post(unit, title, content, picture, picture_name, parent_post=None, 
	assigned_to=None, status=None, event_datetime=None):
	
	access = get_access(unit)
	if not access.get("write"):
		raise webnotes.PermissionError

	unit = webnotes.doc("Unit", unit)	
	post = webnotes.bean({
		"doctype":"Post",
		"title": title.title(),
		"content": content,
		"unit": unit.name,
		"parent_post": parent_post or None
	})
	
	if unit.unit_type == "Tasks":
		post.doc.is_task = 1
		post.doc.assigned_to = assigned_to
	elif unit.unit_type == "Events":
		post.doc.is_event = 1
		post.doc.event_datetime = event_datetime
	
	post.ignore_permissions = True
	post.insert()

	if picture_name and picture:
		process_picture(post, picture_name, picture)
	
	# send email
	if parent_post:
		post.run_method("send_email_on_reply")
		
@webnotes.whitelist(allow_guest=True)
def save_post(post, title, content, picture, picture_name,
	assigned_to=None, status=None, event_datetime=None):
	
	post = webnotes.bean("Post", post)

	access = get_access(post.doc.unit)
	if not access.get("write"):
		raise webnotes.PermissionError
	
	# TODO improve error message
	if webnotes.session.user != post.doc.owner:
		for fieldname in ("title", "content"):
			if post.doc.fields.get(fieldname) != locals().get(fieldname):
				webnotes.throw("You cannot change: {}".format(fieldname.title()))
				
		if picture and picture_name:
			webnotes.throw("You cannot change: Picture")
			
	post.doc.fields.update({
		"title": title.title(),
		"content": content,
		"assigned_to": assigned_to,
		"status": status,
		"event_datetime": event_datetime
	})
	post.ignore_permissions = True
	post.save()
	
	if picture_name and picture:
		process_picture(post, picture_name, picture)
		
def process_picture(post, picture_name, picture):
	file_data = save_file(picture_name, picture, "Post", post.doc.name, decode=True)
	post.doc.picture_url = file_data.file_name or file_data.file_url
	webnotes.conn.set_value("Post", post.doc.name, "picture_url", post.doc.picture_url)
	clear_unit_views(unit.name)
	
@webnotes.whitelist()
def assign_post(post, profile=None):
	post = get_post_for_write(post)
	
	if profile and not get_access(post.doc.unit, profile).get("write"):
		raise webnotes.PermissionError("Selected user does not have 'write' access to this post")
		
	if profile and post.doc.assigned_to:
		webnotes.throw("Someone is already assigned to this post. Please refresh.")
		
	if not profile and post.doc.status == "Completed":
		webnotes.throw("You cannot revoke assignment of a completed task.")
		
	post.doc.status = "Assigned" if profile else None
	
	post.doc.assigned_to = profile
	post.doc.assigned_to_fullname = get_fullname(profile) if profile else None
	
	post.ignore_permissions = True
	post.save()
	
	return {
		"post_settings_html": get_post_settings(post.doc.unit, post.doc.name),
		"assigned_to_fullname": post.doc.assigned_to_fullname,
		"status": post.doc.status
	}

@webnotes.whitelist()
def set_event(post, event_datetime):
	post = get_post_for_write(post)
		
	post.doc.event_datetime = event_datetime
	post.ignore_permissions = True
	post.save()
	
	return get_post_settings(post.doc.unit, post.doc.name)
	
@webnotes.whitelist()
def update_task_status(post, status):
	post = get_post_for_write(post)

	if post.doc.assigned_to and status:
		post.doc.status = status
		post.ignore_permissions = True
		post.save()
	
	return {
		"post_settings_html": get_post_settings(post.doc.unit, post.doc.name),
		"status": post.doc.status
	}

def get_post_for_write(post):
	post = webnotes.bean("Post", post)

	if not get_access(post.doc.unit).get("write"):
		raise webnotes.PermissionError("You are not allowed edit this post")
		
	return post
	
@webnotes.whitelist()
def suggest_user(unit, term):
	"""suggest a user that has read permission in this unit tree"""
	profiles = webnotes.conn.sql("""select 
		pr.name, pr.first_name, pr.last_name, 
		pr.user_image, pr.fb_location, pr.fb_hometown
		from `tabProfile` pr
		where (pr.first_name like %(term)s or pr.last_name like %(term)s)
		and pr.name not in ("Guest", "Administrator") is not null and pr.enabled=1""", 
		{"term": "%{}%".format(term), "unit": unit}, as_dict=True)
	
	template = webnotes.get_template("templates/includes/profile_display.html")
	return [{
		"value": "{} {}".format(pr.first_name or "", pr.last_name or "").strip(), 
		"profile_html": template.render({"unit_profile": pr}),
		"profile": pr.name
	} for pr in profiles]

	