# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

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
			"parent_unit": parent_unit, "unit_type": unit_type, "public":1}).insert())
		
		for det in ((children_name, "Public"), ("Forum", "Public"), ("Discussion", "Private")):
			units.append(webnotes.bean({
				"doctype":"Unit", 
				"parent_unit": units[0].doc.name, 
				"unit_type": unit_type, 
				"unit_title": det[0],
				"public": 1 if det[1]=="Public" else 0,
				"unit_name": unit_name + "-" + det[0]
			}).insert())
		return units
	
	india = create_units("India", "India", "", "States", "Country")
		
	for state in data:
		state_units = create_units(state, state, india[1].doc.name, "Districts", "State")
		for district in data[state]:
			district_units = create_units(state_units[0].doc.name + "-" + district, district, state_units[1].doc.name, 
				"Blocks", "District")
			
			for block in data[state][district] or []:
				block_unit = create_units(district_units[0].doc.name + "-" + block, block, district_units[1].doc.name, 
					"Primary", "Block")
				
	webnotes.conn.commit()

	