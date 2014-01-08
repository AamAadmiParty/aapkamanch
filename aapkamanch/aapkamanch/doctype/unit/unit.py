# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes

from webnotes.utils.nestedset import DocTypeNestedSet

class DocType(DocTypeNestedSet):
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
		
	def autoname(self):
		self.doc.name = self.doc.unit_name
		print self.doc.name
		
	def validate(self):
		self.remove_no_rules_with_no_perms()
		
	def remove_no_rules_with_no_perms(self):
		to_remove = []
		for i, d in enumerate(self.doclist.get({"doctype":"Unit Profile"})):
			if not (d.read or d.write or d.admin):
				to_remove.append(d)
				
		for d in to_remove:
			self.doclist.remove(d)
			
	def on_update(self):
		DocTypeNestedSet.on_update(self)
		cache = webnotes.cache()
		for key in ("is_public", "unit_html"):
			cache.delete_value(key + ":" + self.doc.name)
		