# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes
from aapkamanch.templates.unit_templates.forum_feed import get_post_list_html

def get_unit_html(context):
	context["post_list_html"] = get_post_list_html(context.get("name"), context.get("view"))