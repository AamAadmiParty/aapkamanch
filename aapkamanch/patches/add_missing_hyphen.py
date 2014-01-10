import webnotes

def execute():
	webnotes.conn.sql("""update tabUnit 
		set name=replace(name, " ", "-"),
		parent_unit = replace(parent_unit, " ", "-"),
		old_parent = replace(old_parent, " ", "-")""")
		
	webnotes.conn.sql("""update `tabUnit Profile` 
		set parent=replace(parent, " ", "-")""")

	webnotes.conn.sql("""update `tabPost` 
		set unit=replace(unit, " ", "-")""")		