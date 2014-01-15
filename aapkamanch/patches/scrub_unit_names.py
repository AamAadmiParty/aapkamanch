import webnotes

def execute():
	webnotes.conn.sql("""update tabUnit 
		set name=replace(LOWER(name), "&", "and"),
		parent_unit = replace(LOWER(parent_unit), "&", "and"),
		old_parent = replace(LOWER(old_parent), "&", "and")""")
		
	webnotes.conn.sql("""update `tabUnit Profile` 
		set parent=replace(LOWER(parent), "&", "and")""")

	webnotes.conn.sql("""update `tabPost` 
		set unit=replace(LOWER(unit), "&", "and")""")