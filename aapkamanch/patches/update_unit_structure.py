from __future__ import unicode_literals
import webnotes

def execute():
	# rename columns
	columns = webnotes.conn.get_table_columns("Unit")
	
	if "public" in columns:
		if "public_read" not in columns:
			webnotes.conn.sql_ddl("alter table `tabUnit` change public public_read int(1) default null")
		elif webnotes.conn.sql("select count(*) from `tabUnit` where public_read=1")[0][0]==0:
			webnotes.conn.sql("""update `tabUnit` set public_read=public""")
		
	if "forum" in columns:
		if "public_write" not in columns:
			webnotes.conn.sql_ddl("alter table `tabUnit` change forum public_write int(1) default null")
		elif webnotes.conn.sql("select count(*) from `tabUnit` where public_write=1")[0][0]==0:
			webnotes.conn.sql("""update `tabUnit` set public_write=forum""")
	
	webnotes.reload_doc("aapkamanch", "doctype", "unit")
	
	webnotes.conn.sql("update `tabUnit` set unit_type='Forum'")
	
	
	
	