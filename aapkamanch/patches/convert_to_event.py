from __future__ import unicode_literals
import webnotes

def execute():
	# set is_task = 1 where assigned
	webnotes.reload_doc("aapkamanch", "doctype", "post")
	webnotes.conn.sql("""update `tabPost` set is_event=1 where ifnull(event_datetime, '')!=''""")
