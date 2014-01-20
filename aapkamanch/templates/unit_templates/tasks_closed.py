# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes
from aapkamanch.helpers import get_access
from aapkamanch.templates.unit_templates.tasks_open import get_task_list_html

def get_unit_html(context):
	print "here!"
	context["task_list_html"] = get_task_list_html(context.get("name"), view=context.get("view"), status="Closed")