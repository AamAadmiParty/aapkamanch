from __future__ import unicode_literals
import frappe
from frappe.utils import strip_html
from frappe.utils.email_lib.html2text import html2text

def execute():
	frappe.reload_doc("aapkamanch", "doctype", "post")
	
	frappe.conn.sql("""update `tabPost` set status='Open' where status='Assigned'""")
	frappe.conn.sql("""update `tabPost` set status='Closed' where status='Completed'""")
	
	for name, content in frappe.conn.sql("""select name, content from `tabPost`"""):
		# extract text, strip and remove new lines and spaces
		title = html2text(content)
		title = title.strip().replace("\n", " ").replace("  ", " ")
		title = title[:100] + ("..." if len(title) > 100 else "")
		frappe.conn.set_value("Post", name, "title", title)