# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import frappe, json

@frappe.whitelist()
def import_groups():
	"""rebuild all groups from groups.json"""
	frappe.conn.sql("""delete from `tabPost`""")
	frappe.conn.sql("""delete from `tabWebsite Group`""")
	frappe.conn.sql("""delete from `tabWebsite Sitemap` where ref_doctype='Website Group'""")
	
	frappe.conn.auto_commit_on_many_writes = True
	
	with open(frappe.get_pymodule_path("aapkamanch", "data", "groups.json")) as f:
		data = json.loads(f.read())
		
	def create_groups(group_name, group_title, parent_website_sitemap):
		group = frappe.bean({
			"doctype":"Website Group", 
			"group_name": group_name, 
			"group_title": group_title,
			"parent_website_sitemap": parent_website_sitemap, 
			"public_read":1, 
			"public_write":1,
			"group_type":"Forum"
		}).insert()
		
		return frappe.conn.get_value("Website Sitemap", {"ref_doctype":"Website Group", 
			"docname": group.doc.name})
			
	india = create_groups("Forum", "Forum", "")

	for state in data:
		state_groups = create_groups(state, state, india)
		for district in data[state]:
			district_groups = create_groups(district, district, state_groups)
			
			# for block in data[state][district] or []:
			# 	block_unit = create_groups(block, block, district_groups)
				
	frappe.conn.commit()

	