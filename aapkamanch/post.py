# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from helpers import get_access

@webnotes.whitelist()
def get_post_list_html(unit, limit_start=0, limit_length=20):
	if webnotes.local.form_dict.cmd=="get_post_list_html":
		# for paging
		if not get_access(unit).get("read"):
			raise webnotes.PermissionError
	
	posts = webnotes.conn.sql("""select p.name,
		p.creation, p.content, pr.fb_username, pr.first_name, pr.last_name 
		from tabPost p, tabProfile pr
		where p.unit=%s and pr.name = p.owner order by p.creation desc limit %s, %s""", 
			(unit, limit_start, limit_length), as_dict=True)
			
	return webnotes.get_template("templates/includes/post_list.html").render({"posts": posts, 
		"limit_start":limit_start})

@webnotes.whitelist()
def add_post(unit, content):
	if not get_access(unit).get("write"):
		raise webnotes.PermissionError
		
	post = webnotes.bean({
		"doctype":"Post",
		"content": content,
		"unit": unit
	})
	post.ignore_permissions = True
	post.insert()
	
	post.doc.fields.update(webnotes.conn.get_value("Profile", webnotes.session.user, 
		["first_name", "last_name", "fb_username"], as_dict=True))
	
	webnotes.cache().delete_value("unit_html:" + unit)
	
	return webnotes.get_template("templates/includes/post.html").render({"post":post.doc.fields})

@webnotes.whitelist()
def get_post_settings(unit, post_name):
	if not get_access(unit).get("write"):
		raise webnotes.PermissionError


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
	