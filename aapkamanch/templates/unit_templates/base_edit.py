# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes

def get_unit_html(context):
	post = webnotes.doc("Post", webnotes.form_dict.name)
	context["session_user"] = webnotes.session.user
	context["post"] = post.fields