# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from helpers import get_views
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

def clear_cache(unit):
	unit = unit.lower()
	clear_unit_views(unit)
	
def clear_unit_views(unit):
	cache = webnotes.cache()
	for key in ("unit_context", "unit_html"):
		for view in get_views(unit):
			cache.delete_value("{key}:{unit}:{view}".format(key=key, unit=unit, view=view.get("view")))

def clear_event_cache():
	for unit in webnotes.conn.sql_list("""select name from `tabUnit` where unit_type='Event'"""):
		clear_cache(unit)

def clear_cache_after_upvote(bean, trigger):
	if bean.doc.ref_doctype != "Post": return
	
	unit = webnotes.conn.get_value(bean.doc.ref_doctype, bean.doc.ref_name, "unit")
	
	for view in get_views(unit):
		if view.get("upvote"):
			clear_cache(unit)
			break
