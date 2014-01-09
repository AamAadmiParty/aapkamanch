# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from permissions import get_access

@webnotes.whitelist()
def add_unit(unit, new_unit, public):
	if not get_access(unit).get("admin"):
		raise webnotes.PermissionError
			
	unit = webnotes.bean({
		"doctype": "Unit",
		"unit_name": unit + "-" + new_unit,
		"unit_title": new_unit,
		"parent_unit": unit,
		"unit_type": "Group",
		"public": int(public)
	})
	unit.ignore_permissions = True
	unit.insert()
	