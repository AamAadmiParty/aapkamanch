# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes

def get_unit_html(context):
	from aapkamanch.templates.unit_templates import base_edit
	base_edit.get_unit_html(context)
	
	if post.assigned_to:
		context["unit_profile"] = webnotes.doc("Profile", post.assigned_to)
	