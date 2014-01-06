# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

@webnotes.whitelist(allow_guest=True)
def get_unit_content(unit_name):
	# TODO: memcache this
	unit = webnotes.doc("Unit", unit_name)
	return {
		"name": unit.name,
		"parent": unit.parent_unit,
		"children": webnotes.conn.sql_list("""select name 
			from tabUnit where parent_unit=%s""", (unit_name))
	}