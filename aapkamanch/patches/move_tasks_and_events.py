from __future__ import unicode_literals
import frappe
from aapkamanch.unit import _add_unit
from aapkamanch.helpers import clear_cache

def execute():
	# should be executed only once!
	move_tasks_and_events()
	clear_cache()
	
def move_tasks_and_events():
	"""move tasks to tasks unit, events to events unit"""
	unit_tasks = dict(frappe.conn.sql("""select parent_unit, name from `tabUnit`
		where unit_type='Tasks'"""))
	unit_events = dict(frappe.conn.sql("""select parent_unit, name from `tabUnit`
		where unit_type='Events'"""))
	
	for post in frappe.conn.sql_list("""select name from `tabPost` 
		where is_task=1 or is_event=1"""):
		post = frappe.bean("Post", post)
		if post.doc.is_task:
			if not unit_tasks.get(post.doc.unit):
				# create unit of type Tasks
				new_unit = _add_unit(post.doc.unit, "Tasks", 1, 1, unit_type="Tasks")
				unit_tasks[post.doc.unit] = new_unit.doc.name
			
			post.doc.unit = unit_tasks.get(post.doc.unit)
			post.doc.is_event = 0
			
		elif post.doc.is_event:
			if not unit_events.get(post.doc.unit):
				# create unit of type Events
				new_unit = _add_unit(post.doc.unit, "Events", 1, 1, unit_type="Events")
				unit_events[post.doc.unit] = new_unit.doc.name
			
			post.doc.unit = unit_events.get(post.doc.unit)
			post.doc.is_task = 0
		
		print post.doc.name
		post.save()