import frappe

def execute():
	frappe.reload_doc("aapkamanch", "doctype", "unit")
	frappe.conn.sql("""update tabUnit set public_write=1 where unit_title='Forum'""")