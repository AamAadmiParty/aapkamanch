# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from aapkamanch.helpers import get_child_unit_items, get_access, get_views

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
			for v, opts in get_views(unit).items():
				if opts.get("default"):
					view = v
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
		views = get_views(unit)
		view_options = views.get(view, {})
		if view_options:
			title += " - " + view_options["label"]
		
		views = sorted([opts for v, opts in views.items()], key=lambda d: d.get("idx"))
		context = {
			"name": unit.name,
			"public_read": unit.public_read,
			"title": "Aam Aadmi Party: " + title,
			"unit_title": title,
			"public_write": unit.public_write,
			"parents": parents,
			"children": get_child_unit_items(unit.name, public_read=1),
			"unit": unit.fields,
			"view": view,
			"views": views,
			"view_options": view_options
		}
		return context
		
	return webnotes.cache().get_value("unit_context:{unit}:{view}".format(unit=unit.lower(), view=view), 
		lambda:_get_unit_context(unit, view))
		
def get_unit_html(context):
	def _get_unit_html(context):
		update_context = context.get("view_options").get("update_context")
		if update_context:
			webnotes.get_attr(update_context)(context)
		
		template = context.get("view_options").get("template")
		return webnotes.get_template(template).render(context)
	
	if context.get("view_options", {}).get("no_cache"):
		return _get_unit_html(context)
	
	return webnotes.cache().get_value("unit_html:{unit}:{view}".format(unit=context.get("name").lower(),
		view=context.get("view")), lambda:_get_unit_html(context))

def has_access(unit, view):
	access = get_access(unit)
	
	if view=="settings":
		return access.get("admin")
	elif view in ("add", "edit"):
		return access.get("write")
	else:
		return access.get("read")