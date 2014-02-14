from __future__ import unicode_literals
import frappe
from frappe.utils.nestedset import rebuild_tree

def execute():
	rename_columns()
	change_unit_type()
	
def rename_columns():
	# rename columns
	columns = frappe.conn.get_table_columns("Unit")
	
	if "public" in columns:
		if "public_read" not in columns:
			frappe.conn.sql_ddl("alter table `tabUnit` change public public_read int(1) default null")
		else:
			frappe.conn.sql("""update `tabUnit` set public_read=`public`""")
		
	if "forum" in columns:
		if "public_write" not in columns:
			frappe.conn.sql_ddl("alter table `tabUnit` change forum public_write int(1) default null")
		else:
			frappe.conn.sql("""update `tabUnit` set public_write=`forum`""")
	
	frappe.reload_doc("aapkamanch", "doctype", "unit")
	
def change_unit_type():
	frappe.conn.sql("update `tabUnit` set unit_type='Forum', public_write=1, public_read=1")
	# print "converted to forum"
	
	frappe.conn.auto_commit_on_many_writes = 1

	# remove Forum, Discussion
	for unit in frappe.conn.sql("""select name, parent_unit from `tabUnit` 
		where unit_title in ('Forum', 'Discussion') order by lft desc""", as_dict=True):
		# print "removing unit", unit

		frappe.conn.sql("""update `tabPost` set unit=%s where unit=%s""", (unit.parent_unit, unit.name))
		frappe.conn.sql("""delete from `tabUnit` where name=%s""", (unit.name,))
		
	rebuild_tree("Unit", "parent_unit")

	frappe.conn.auto_commit_on_many_writes = 0