from __future__ import unicode_literals
import frappe

def execute():
	# set is_task = 1 where assigned
	frappe.reload_doc("aapkamanch", "doctype", "post")
	frappe.conn.sql("""update `tabPost` set is_task=1 where ifnull(assigned_to, '')!=''""")
	frappe.conn.sql("""update `tabPost` set status="Open" where is_task=1 and ifnull(status, '')=''""")