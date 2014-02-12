# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

def after_install():
	from .import_groups import import_groups
	import_groups()
