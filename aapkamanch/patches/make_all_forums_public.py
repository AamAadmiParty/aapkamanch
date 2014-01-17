import webnotes

def execute():
	webnotes.reload_doc("aapkamanch", "doctype", "unit")
	webnotes.conn.sql("""update tabUnit set public_write=1 where unit_title='Forum'""")