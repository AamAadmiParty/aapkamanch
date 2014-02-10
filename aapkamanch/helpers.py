# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json
import os

def get_user_image():
	return webnotes.cache().get_value(webnotes.session.user + ":user_image", 
		lambda: webnotes.conn.get_value("Profile", webnotes.session.user, "user_image"))

def update_website_context(context):
	context.update({
		"total_users": webnotes.cache().get_value("total_users", 
			lambda: str(webnotes.conn.sql("""select count(*) from tabProfile""")[0][0]))
	})
