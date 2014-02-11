# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

def after_install():
	from .import_groups import import_groups
	import_groups()
	
	website_settings = webnotes.bean("Website Settings", "Website Settings")
	website_settings.doc.home_page = "india"
	website_settings.save()
	webnotes.conn.commit()

