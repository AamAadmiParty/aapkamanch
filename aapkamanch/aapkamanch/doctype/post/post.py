# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes

from aapkamanch.helpers import get_access

class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
	
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