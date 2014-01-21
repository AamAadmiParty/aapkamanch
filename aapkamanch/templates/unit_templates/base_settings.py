# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes
from aapkamanch.permissions import get_unit_settings_html

def get_unit_html(context):
	context["unit_settings"] = get_unit_settings_html(context.get("name"))