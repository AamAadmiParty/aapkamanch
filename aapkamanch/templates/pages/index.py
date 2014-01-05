# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

def get_context():
	path = webnotes.request.path[1:]
	if not path: 
		path = "India"
	from aapkamanch.helpers import get_unit_content
	context = get_unit_content(path)
	context.update({"name": path})
	return context