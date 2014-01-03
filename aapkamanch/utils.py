# Copyright Aap Ka Manch
# License GNU General Public Licence

def after_install():
	website_settings = webnotes.bean("Website Settings", "Website Settings")
	website_settings.doc.home_page = "index"
	website_settings.doc.disable_signup = 1
	website_settings.save()
	webnotes.conn.commit()
	