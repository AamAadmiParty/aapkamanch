from __future__ import unicode_literals
import webnotes
from HTMLParser import HTMLParser

def execute():
	webnotes.reload_doc("aapkamanch", "doctype", "post")
	
	webnotes.conn.sql("""update `tabPost` set status='Open' where status='Assigned'""")
	
	for name, content in webnotes.conn.sql("""select name, content from `tabPost`"""):
		# extract text, strip and remove new lines and spaces
		title = strip_tags(content)
		title = title.strip().replace("\n", " ").replace("  ", " ")
		title = title[:100] + ("..." if len(title) > 100 else "")
		webnotes.conn.set_value("Post", name, "title", title)

# http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
	def __init__(self):
		self.reset()
		self.fed = []
	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return ''.join(self.fed)

def strip_tags(html):
	s = MLStripper()
	s.feed(html)
	return s.get_data()