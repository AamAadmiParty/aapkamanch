# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes, re

from webnotes.utils.nestedset import DocTypeNestedSet
from aapkamanch.helpers import clear_unit_cache

class DocType(DocTypeNestedSet):
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
		
	def autoname(self):
		self.validate_name()
		self.doc.name = self.doc.unit_name
		print self.doc.name
		
	def validate(self):
		self.doc.unit_title = self.doc.unit_title.title()
		self.remove_no_rules_with_no_perms()
		self.make_private_if_parent_is_private()
		
	def make_private_if_parent_is_private(self):
		if self.doc.parent_unit and not webnotes.conn.get_value("Unit", self.doc.parent_unit, "public"):
			self.doc.public = 0
	
	def validate_name(self):
		self.doc.unit_name = self.doc.unit_name.strip().lower().replace(" ", "-")
		if re.findall("[^a-zA-Z1-9-]", self.doc.unit_name):
			raise webnotes.PermissionError
	
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
		for key in ("is_public", "unit_title"):
			cache.delete_value(key + ":" + self.doc.name)
			
		clear_unit_cache("unit_html", self.doc.name)
		clear_unit_cache("unit_context", self.doc.name)