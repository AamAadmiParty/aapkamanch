# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes
from aapkamanch.templates.unit_templates.events_upcoming import get_event_list_html

def get_unit_html(context):
	context["event_list_html"] = get_event_list_html(context.get("name"), view=context.get("view"))