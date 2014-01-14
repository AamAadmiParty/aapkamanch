from __future__ import unicode_literals
import webnotes

def execute():
	webnotes.conn.sql("""update `tabProfile` set user_type='Website User' where fb_username is not null""")