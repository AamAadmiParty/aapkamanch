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
	
def import_states_and_districts():
	with open(webnotes.get_pymodule_path("aapkamanch", "data", "loksabha.json")) as f:
		data = json.loads(f.read())
		
	for state in data:
		webnotes.bean({"doctype":"State", "state_name": state}).insert()
		for district in data[state]:
			webnotes.bean({"doctype":"District", "state": state, "district_name":district}).insert()
		webnotes.conn.commit()
	