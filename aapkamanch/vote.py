# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from permissions import get_access

@webnotes.whitelist()
def set_vote(ref_doctype, ref_name):
	try:
		user_vote = webnotes.bean({
			"doctype": "User Vote",
			"ref_doctype": ref_doctype,
			"ref_name": ref_name
		})
		user_vote.ignore_permissions = True
		user_vote.insert()
		return "ok"
	except webnotes.DuplicateEntryError:
		return "duplicate"
		