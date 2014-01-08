# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from aapkamanch.helpers import get_child_unit_items, get_access, is_public
from aapkamanch.post import get_post_list_html

no_cache = True

def get_context():
	unit = webnotes.request.path[1:]
	try:
		if not unit or unit.lower().split(".")[0]=="index":
			unit = "India"
		
		if not is_public(unit):
			if not get_access(unit).get("read"):
				raise webnotes.PermissionError
		
		return {"content": get_unit_html(unit)}
	except webnotes.DoesNotExistError:
		return {"content": '<div class="alert alert-danger full-page">The page you are looking for does not exist.</div>'}
	except webnotes.PermissionError:
		return {"content": '<div class="alert alert-danger full-page">You are not permitted to view this page.</div>'}
	
def get_unit_html(unit):
	def _get_unit_html(unit):
		unit = webnotes.doc("Unit", unit)

		context = {
			"name": unit.name,
			"public": unit.public,
			"title": unit.unit_title,
			"parent": unit.parent_unit,
			"parent_title": webnotes.conn.get_value("Unit", unit.parent_unit, "unit_title"),
			"children": get_child_unit_items(unit.name, public=1),
			"post_list_html": get_post_list_html(unit.name)
		}
	
		return webnotes.get_template("templates/includes/unit.html").render(context)

	return _get_unit_html(unit)
	#return webnotes.cache().get_value("unit_html:" + unit, lambda:_get_unit_html(unit))

