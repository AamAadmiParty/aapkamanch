from __future__ import unicode_literals
import webnotes
from webnotes.website import rebuild_config
from webnotes.webutils import cleanup_page_name

def execute():
	# move fb data from custom to profile fields
	webnotes.conn.sql("""update `tabProfile` set location=fb_location, bio=fb_bio""")
	
	# rebuild website sitemap config
	rebuild_config()
	
	# move unit data to website group and unit profile to website sitemap permission
	for unit in webnotes.conn.sql_list("""select name from `tabUnit` order by lft"""):
		migrate_unit_to_website_group(unit)
		
	webnotes.delete_doc("DocType", "Unit")
	webnotes.delete_doc("DocType", "Unit Profile")
	
def migrate_unit_to_website_group(unit):
	unit = webnotes.bean("Unit", unit)
	
	if webnotes.conn.get_value("Website Group", cleanup_page_name(unit.doc.name)):
		# already exists!
		return
	
	unit_name = cleanup_page_name(unit.doc.name)
	print unit_name
	
	# create website group
	group = webnotes.new_bean("Website Group")
	group.doc.group_name = unit.doc.name
	group.doc.group_title = unit.doc.unit_title
	group.doc.group_type = unit.doc.unit_type
	group.doc.group_description = unit.doc.unit_description
	group.doc.public_read = unit.doc.public_read
	group.doc.public_write = unit.doc.public_write
	group.doc.upvotes = unit.doc.upvotes
	group.doc.replies = unit.doc.replies
	
	if unit.doc.parent_unit:
		parent_docname = cleanup_page_name(unit.doc.parent_unit)
		group.doc.parent_website_sitemap = webnotes.conn.get_value("Website Sitemap",
			{"ref_doctype": "Website Group", "docname": parent_docname})
			
		# just making sure if my logic is correct!
		if not group.doc.parent_website_sitemap:
			if parent_docname.endswith("discussion"):
				print "ignoring", unit_name
				return
			
			raise Exception("Website Sitemap Not Found: {}".format(unit.doc.parent_unit))
	
	group.insert()
	
	# add website sitemap permissions
	for d in unit.doclist.get({"doctype": "Unit Profile"}):
		webnotes.bean({
			"doctype": "Website Sitemap Permission",
			"website_sitemap": group.doc.page_name,
			"profile": d.profile,
			"read": d.read,
			"write": d.write,
			"admin": d.admin
		}).insert()
	
	# move posts
	webnotes.conn.sql("""update `tabPost` set website_group=%s where unit=%s""", (group.doc.name,
		unit.doc.name))
	
	# WARNING - commit here to avoid too many writes error!
	webnotes.conn.commit()
