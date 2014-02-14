# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import frappe, json
import os

def get_user_image():
	return frappe.cache().get_value(frappe.session.user + ":user_image", 
		lambda: frappe.conn.get_value("Profile", frappe.session.user, "user_image"))

def update_website_context(context):
	context.update({
		"total_users": frappe.cache().get_value("total_users", 
			lambda: str(frappe.conn.sql("""select count(*) from tabProfile""")[0][0]))
	})
