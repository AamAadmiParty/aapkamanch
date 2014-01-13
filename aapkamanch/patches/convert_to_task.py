from __future__ import unicode_literals
import webnotes

def execute():
	# set is_task = 1 where assigned
	webnotes.reload_doc("aapkamanch", "doctype", "post")
	webnotes.conn.sql("""update `tabPost` set is_task=1 where ifnull(assigned_to, '')!=''""")
	webnotes.conn.sql("""update `tabPost` set status="Open" where is_task=1 and ifnull(status, '')=''""")