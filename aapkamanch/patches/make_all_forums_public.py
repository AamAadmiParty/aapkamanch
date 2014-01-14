import webnotes

def execute():
	webnotes.reload_doc("aapkamanch", "doctype", "unit")
	webnotes.conn.sql("""update tabUnit set forum=1 where unit_title='Forum'""")