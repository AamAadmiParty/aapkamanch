# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from permissions import get_access

@webnotes.whitelist()
def add_unit(unit, new_unit, public_read, public_write, unit_type="Forum"):
	if not get_access(unit).get("admin"):
		raise webnotes.PermissionError
			
	unit = webnotes.bean({
		"doctype": "Unit",
		"unit_name": unit + "-" + new_unit,
		"unit_title": new_unit,
		"parent_unit": unit,
		"unit_type": unit_type,
		"public_read": int(public_read),
		"public_write": int(public_write)
	})
	unit.ignore_permissions = True
	unit.insert()

@webnotes.whitelist()
def update_description(unit, description):
	if not get_access(unit).get("admin"):
		raise webnotes.PermissionError

	unit = webnotes.bean("Unit", unit)
	unit.doc.unit_description = description
	unit.ignore_permissions = True
	unit.save()
