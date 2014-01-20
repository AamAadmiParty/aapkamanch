# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from permissions import get_access

@webnotes.whitelist()
def set_vote(ref_doctype, ref_name):
	try:
		webnotes.bean({
			"doctype": "User Vote",
			"ref_doctype": ref_doctype,
			"ref_name": ref_name
		}).insert()
		return "ok"
	except webnotes.DuplicateEntryError:
		return "duplicate"
		