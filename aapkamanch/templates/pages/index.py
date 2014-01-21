# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from aapkamanch.helpers import get_child_unit_items, get_access, get_views, get_view_options

no_cache = True

def get_context():
	view = None
	unit = webnotes.request.path[1:]
	try:
		if not unit or unit.lower().split(".")[0]=="index":
			unit = "India"
		
		if "/" in unit:
			unit, view = unit.split("/", 1)
			
		if not view:
			for v in get_views(unit):
				if v.get("default"):
					view = v["view"]
					break
		
		if not has_access(unit, view):
			raise webnotes.PermissionError
		
		context = get_unit_context(unit, view)
		context["content"] = get_unit_html(context)
		context["access"] = get_access(unit)
				
		return context
		
	except webnotes.DoesNotExistError:
		return {"content": '<div class="alert alert-danger full-page">The page you are looking for does not exist.</div>'}
	except webnotes.PermissionError:
		return {"content": '<div class="alert alert-danger full-page">You are not permitted to view this page.</div>'}
		
def get_unit_context(unit, view):
	def _get_unit_context(unit, view):
		unit = webnotes.doc("Unit", unit)
		
		parents = webnotes.conn.sql("""select name, unit_title from tabUnit 
			where lft < %s and rgt > %s order by lft asc""", (unit.lft, unit.rgt), as_dict=1)
		
		# update title
		title = unit.unit_title
		unit_views = get_views(unit)
		unit_views_map = dict((d["view"], d) for d in unit_views)
		if view in unit_views_map:
			title += " - " + unit_views_map[view]["label"]
			# parents += [{"name": unit.name, "unit_title": unit.unit_title}]
				
		context = {
			"name": unit.name,
			"unit_description": unit.unit_description,
			"public_read": unit.public_read,
			"unit_title": title,
			"public_write": unit.public_write,
			"parents": parents,
			"children": get_child_unit_items(unit.name, public_read=1),
			"unit": unit.fields,
			"view": view,
			"views": get_views(unit),
			"view_options": get_view_options(unit, view)
		}
		return context
		
	return webnotes.cache().get_value("unit_context:{unit}:{view}".format(unit=unit.lower(), view=view), 
		lambda:_get_unit_context(unit, view))
		
def get_unit_html(context):
	def _get_unit_html(context):
		try:
			try:
				method = "aapkamanch.templates.unit_templates.{unit_type}_{view}.get_unit_html"\
					.format(unit_type=context.get("unit").unit_type.lower(), view=context.get("view").lower())
			
				# method updates context
				webnotes.get_attr(method)(context)
				
			except ImportError:
				# method not found, try base template
				method = "aapkamanch.templates.unit_templates.base_{view}.get_unit_html"\
					.format(view=context.get("view").lower())
				
				# method updates context
				webnotes.get_attr(method)(context)
				
		except ImportError:
			# method not found
			pass
			
		unit_template = get_template(context.get("unit").get("unit_type"), context.get("view"))
		return unit_template.render(context)
	
	if context.get("view_options", {}).get("no_cache"):
		return _get_unit_html(context)
	
	return webnotes.cache().get_value("unit_html:{unit}:{view}".format(unit=context.get("name").lower(),
		view=context.get("view")), lambda:_get_unit_html(context))
		
def get_template(unit_type, view):
	return webnotes.get_template("templates/unit_templates/{}_{}.html".format(unit_type.lower(), view.lower()))

def has_access(unit, view):
	access = get_access(unit)
	
	if view=="settings":
		return access.get("admin")
	elif view in ("add", "edit"):
		return access.get("write")
	else:
		return access.get("read")