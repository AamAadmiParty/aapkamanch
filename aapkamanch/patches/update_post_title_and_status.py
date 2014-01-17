from __future__ import unicode_literals
import webnotes
from webnotes.utils import strip_html

def execute():
	webnotes.reload_doc("aapkamanch", "doctype", "post")
	
	webnotes.conn.sql("""update `tabPost` set status='Open' where status='Assigned'""")
	
	for name, content in webnotes.conn.sql("""select name, content from `tabPost`"""):
		# extract text, strip and remove new lines and spaces
		title = strip_html(content)
		title = title.strip().replace("\n", " ").replace("  ", " ")
		title = title[:100] + ("..." if len(title) > 100 else "")
		webnotes.conn.set_value("Post", name, "title", title)