# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json
from webnotes.core.page.data_import_tool import data_import_tool

def after_install():
	# import custom fields
	data_import_tool.import_doclist(webnotes.get_pymodule_path("aapkamanch", "data", "custom_fields.csv"), 
		overwrite=True)
	
	from .import_units import import_units
	import_units()
	
	website_settings = webnotes.bean("Website Settings", "Website Settings")
	website_settings.doc.home_page = "index"
	website_settings.doc.disable_signup = 1
	website_settings.save()
	webnotes.conn.commit()

