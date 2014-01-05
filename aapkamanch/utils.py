# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

def after_install():
	import_units()
	
	website_settings = webnotes.bean("Website Settings", "Website Settings")
	website_settings.doc.home_page = "index"
	website_settings.doc.disable_signup = 1
	website_settings.save()
	webnotes.conn.commit()

@webnotes.whitelist()
def import_units():
	"""rebuild all units from units.json"""
	webnotes.conn.sql("""delete from tabUnit""")
	webnotes.conn.auto_commit_on_many_writes = True
	
	with open(webnotes.get_pymodule_path("aapkamanch", "data", "units.json")) as f:
		data = json.loads(f.read())

	def create_units(unit_name, unit_title, parent_unit, children_name, unit_type):
		units = []
		units.append(webnotes.bean({"doctype":"Unit", "unit_name": unit_name, "unit_title":unit_title,
			"parent_unit": parent_unit, "unit_type": unit_type}).insert())
		
		for suffix in ("Members", "Office Bearers", children_name):
			units.append(webnotes.bean({"doctype":"Unit", "parent_unit": units[0].doc.name, 
				"unit_type": unit_type, "unit_title": unit_title + "-" + suffix,
				"unit_name": unit_name + "-" + suffix}).insert())
			
		return units
	
	india = create_units("India", "India", "", "States", "Country")
		
	for state in data:
		state_units = create_units(state, state, india[3].doc.name, "Districts", "State")
		for district in data[state]:
			district_units = create_units(state_units[0].doc.name + "-" + district, district, state_units[3].doc.name, 
				"Blocks", "District")
			
			for block in data[state][district] or []:
				block_unit = create_units(district_units[0].doc.name + "-" + block, block, district_units[3].doc.name, 
					"Primary", "Block")
				
	webnotes.conn.commit()

	