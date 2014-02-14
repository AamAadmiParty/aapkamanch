from __future__ import unicode_literals
import frappe

def execute():
	frappe.conn.sql("""update `tabProfile` set user_type='Website User' where fb_username is not null""")