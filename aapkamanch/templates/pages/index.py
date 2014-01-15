# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from aapkamanch.helpers import get_child_unit_items, get_access, is_public
from aapkamanch.permissions import get_unit_settings_html
from aapkamanch.post import get_post_list_html

no_cache = True

def get_context():
	view = None
	unit = webnotes.request.path[1:]
	try:
		if not unit or unit.lower().split(".")[0]=="index":
			unit = "India"
		
		if "/" in unit:
			unit, view = unit.split("/", 1)
			
		if not is_public(unit):
			if not get_access(unit).get("read"):
				raise webnotes.PermissionError
				
		if not view:
			view = "feed"
		
		unit_context = get_unit_context(unit, view)
		
		unit_context.update({
			"title": "Aam Aadmi Party: " + get_unit_title(unit),
			"content": get_unit_html(unit_context, view)
		})
		
		return unit_context
		
	except webnotes.DoesNotExistError:
		return {"content": '<div class="alert alert-danger full-page">The page you are looking for does not exist.</div>'}
	except webnotes.PermissionError:
		return {"content": '<div class="alert alert-danger full-page">You are not permitted to view this page.</div>'}

def get_unit_context(unit, view):
	def _get_unit_context(unit, view):
		unit = webnotes.doc("Unit", unit)
		
		parents = webnotes.conn.sql("""select name, unit_title from tabUnit 
			where lft < %s and rgt > %s order by lft asc""", (unit.lft, unit.rgt), as_dict=1)
		
		title = unit.unit_title
		if view!="feed":
			title += ": {}".format(view.title())
			parents += [{"name": unit.name, "unit_title": unit.unit_title}]
		
		return {
			"name": unit.name,
			"public": unit.public,
			"unit_title": title,
			"forum": unit.forum,
			"parents": parents,
			"children": get_child_unit_items(unit.name, public=1),
			"view": view
		}
		
	return webnotes.cache().get_value("unit_context:{unit}:{view}".format(unit=unit.lower(), view=view), 
		lambda:_get_unit_context(unit, view))

# unit_template = None
def get_unit_html(context, view):
	# global unit_template
	# if not unit_template:
	unit_template = webnotes.get_template("templates/includes/unit.html")
	
	def _get_unit_html(context, view):
		if view=="settings":
			context["unit_settings"] = get_unit_settings_html(context.get("name"))
		else:
			context["post_list_html"] = get_post_list_html(context.get("name"), view=view)
		
		return unit_template.render(context)
	
	return webnotes.cache().get_value("unit_html:{unit}:{view}".format(unit=context.get("name"), view=view), 
		lambda:_get_unit_html(context, view))

def get_unit_title(unit_name):
	def _get_unit_title(unit_name):
		unit = webnotes.conn.get_value("Unit", unit_name, ["unit_title", "parent_unit", "unit_type"], as_dict=1)
		title = unit.unit_title
		if unit.parent_unit and unit.unit_type in ("Group", "Forum"):
			title = webnotes.conn.get_value("Unit", unit.parent_unit, "unit_title") + " " + title
			
		return title
	
	return webnotes.cache().get_value("unit_title:" + unit_name, lambda: _get_unit_title(unit_name))
