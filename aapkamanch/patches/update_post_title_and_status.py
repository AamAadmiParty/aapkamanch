from __future__ import unicode_literals
import webnotes
from webnotes.utils import strip_html
from webnotes.utils.email_lib.html2text import html2text

def execute():
	webnotes.reload_doc("aapkamanch", "doctype", "post")
	
	webnotes.conn.sql("""update `tabPost` set status='Open' where status='Assigned'""")
	webnotes.conn.sql("""update `tabPost` set status='Closed' where status='Completed'""")
	
	for name, content in webnotes.conn.sql("""select name, content from `tabPost`"""):
		# extract text, strip and remove new lines and spaces
		title = html2text(content)
		title = title.strip().replace("\n", " ").replace("  ", " ")
		title = title[:100] + ("..." if len(title) > 100 else "")
		webnotes.conn.set_value("Post", name, "title", title)