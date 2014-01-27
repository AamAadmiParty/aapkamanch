# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from helpers import get_access, clear_permissions
from webnotes.utils.email_lib.bulk import send

def get_unit_settings_html(unit):
	if not get_access(unit).get("admin"):
		raise webnotes.PermissionError
	
	unit_profiles = webnotes.conn.sql("""select pr.first_name, pr.last_name, 
		pr.user_image, pr.fb_location, pr.fb_hometown, up.profile,
		up.`read`, up.`write`, up.`admin`
		from tabProfile pr, `tabUnit Profile` up 
		where up.profile = pr.name and up.parent=%s""", (unit,), as_dict=1)
	
	unit = webnotes.conn.get_value("Unit", unit, ["public_read", "public_write", "unit_description"], as_dict=True)
	
	return webnotes.get_template("templates/includes/unit_settings.html").render({
		"public_read": unit.public_read,
		"public_write": unit.public_write,
		"unit_description": unit.unit_description,
		"unit_profiles": unit_profiles
	})

@webnotes.whitelist()
def suggest_user(term, unit):
	profiles = webnotes.conn.sql("""select pr.name, pr.first_name, pr.last_name, 
		pr.user_image, pr.fb_location, pr.fb_hometown
		from `tabProfile` pr 
		where (pr.first_name like %(term)s or pr.last_name like %(term)s)
		and pr.user_image is not null and pr.enabled=1
		and not exists(select up.parent from `tabUnit Profile` up 
			where up.parent=%(unit)s and up.profile=pr.name)""", 
		{"term": "%{}%".format(term), "unit": unit}, as_dict=True)
	
	template = webnotes.get_template("templates/includes/profile_display.html")
	return [{
		"value": "{} {}".format(pr.first_name, pr.last_name), 
		"profile_html": template.render({"unit_profile": pr}),
		"profile": pr.name
	} for pr in profiles]

@webnotes.whitelist()
def add_unit_profile(unit, profile):
	if not get_access(unit).get("admin"):
		raise webnotes.PermissionError
	
	unit = webnotes.bean("Unit", unit)
	unit.doclist.append({
		"doctype": "Unit Profile",
		"parentfield": "unit_profiles",
		"profile": profile,
		"read": 1
	})
	unit.ignore_permissions = True
	unit.save()
	
	clear_permissions(profile)
	
	unit_profile = unit.doclist[-1].fields
	unit_profile.update(webnotes.conn.get_value("Profile", unit_profile.profile, 
		["first_name", "last_name", "user_image", "fb_location", "fb_hometown"], as_dict=True))
	
	return webnotes.get_template("templates/includes/unit_profile.html").render({
		"unit_profile": unit_profile
	})

@webnotes.whitelist()
def update_permission(unit, profile, perm, value):
	if not get_access(unit).get("admin"):
		raise webnotes.PermissionError

	unit = webnotes.bean("Unit", unit)
	unit.doclist.get({"profile":profile})[0].fields[perm] = int(value)
	unit.ignore_permissions = True
	unit.save()
	
	if perm=="admin" and int(value):
		subject = "You have been made Administrator of Group " + unit.doc.name.replace("-", " ").title()
		
		send(recipients=[profile], 
			subject= subject, add_unsubscribe_link=False,
			message="""<h3>Group Notification<h3>\
			<p>%s</p>\
			<p style="color: #888">This is just for your information.</p>""" )

	clear_permissions(profile)
