# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

from permissions import get_access

# don't allow guest to give vote
@webnotes.whitelist()
def set_vote(ref_doctype, ref_name):
	unit = webnotes.conn.get_value(ref_doctype, ref_name, "unit")
	if not get_access(unit).get("read"):
		raise webnotes.PermissionError
	
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
		