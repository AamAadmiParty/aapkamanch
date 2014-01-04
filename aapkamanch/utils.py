# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

def after_install():
	import_states_and_districts()
	
	website_settings = webnotes.bean("Website Settings", "Website Settings")
	website_settings.doc.home_page = "index"
	website_settings.doc.disable_signup = 1
	website_settings.save()
	webnotes.conn.commit()

@webnotes.whitelist()
def import_states_and_districts():
	webnotes.conn.sql("""delete from tabUnit""")
	with open(webnotes.get_pymodule_path("aapkamanch", "data", "loksabha.json")) as f:
		data = json.loads(f.read())
	
	webnotes.bean({"doctype":"Unit", "unit_name":"India", 
		"children_name":"States", "unit_type":"Country"}).insert()
		
	for state in data:
		webnotes.bean({"doctype":"Unit", "unit_name": state, "parent_unit": "India",
			"children_name": "Districts", "unit_type":"State"}).insert()
		for district in data[state]:
			try:
				webnotes.bean({"doctype":"Unit", "unit_type":"District",
					"parent_unit": state, "unit_name":district}).insert()
			except NameError:
				webnotes.bean({"doctype":"Unit", "unit_type":"District",
					"parent_unit": state, "unit_name":district + " - " + "District"}).insert()
				
	webnotes.conn.commit()
	