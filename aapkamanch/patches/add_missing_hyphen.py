import frappe

def execute():
	frappe.conn.sql("""update tabUnit 
		set name=replace(name, " ", "-"),
		parent_unit = replace(parent_unit, " ", "-"),
		old_parent = replace(old_parent, " ", "-")""")
		
	frappe.conn.sql("""update `tabUnit Profile` 
		set parent=replace(parent, " ", "-")""")

	frappe.conn.sql("""update `tabPost` 
		set unit=replace(unit, " ", "-")""")