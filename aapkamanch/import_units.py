# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

@webnotes.whitelist()
def import_groups():
	"""rebuild all groups from groups.json"""
	webnotes.conn.sql("""delete from `tabWebsite Group`""")
	webnotes.conn.auto_commit_on_many_writes = True
	
	with open(webnotes.get_pymodule_path("aapkamanch", "data", "groups.json")) as f:
		data = json.loads(f.read())

	def create_groups(group_name, group_title, parent_website_group, children_name):
		groups = []
		groups.append(webnotes.bean({"doctype":"Website Group", "group_name": group_name, "group_title":group_title,
			"parent_website_group": parent_website_group, "public_read":1, "public_write": 1}).insert())
		
		for det in (children_name,):
			groups.append(webnotes.bean({
				"doctype":"Website Group", 
				"parent_website_group": groups[0].doc.name, 
				"group_type": "Forum", 
				"group_title": det,
				"public_read": 1,
				"public_write": 1,
				"group_name": group_name + "-" + det
			}).insert())
		return groups
	
	india = create_groups("India", "India", "", "States")
		
	for state in data:
		state_groups = create_groups(state, state, india[1].doc.name, "Districts")
		for district in data[state]:
			district_groups = create_groups(state_groups[0].doc.name + "-" + district, district, state_groups[1].doc.name, 
				"Blocks")
			
			for block in data[state][district] or []:
				block_unit = create_groups(district_groups[0].doc.name + "-" + block, block, district_groups[1].doc.name, 
					"Primary")
				
	webnotes.conn.commit()

	