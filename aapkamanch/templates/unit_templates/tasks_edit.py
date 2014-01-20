# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes
from aapkamanch.helpers import get_access

def get_unit_html(context):
	if not get_access(context.get("unit")["name"]):
		raise webnotes.PermissionError
	
	post = webnotes.doc("Post", webnotes.form_dict.name)
	context["session_user"] = webnotes.session.user
	if post.assigned_to:
		context["unit_profile"] = webnotes.doc("Profile", post.assigned_to)
		
	context["post"] = post.fields