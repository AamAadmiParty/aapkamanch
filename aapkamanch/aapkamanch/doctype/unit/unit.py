# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes, re

from aapkamanch.unit import clear_unit_views
from webnotes.utils.nestedset import DocTypeNestedSet

class DocType(DocTypeNestedSet):
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
		self.nsm_parent_field = "parent_unit"
		
	def autoname(self):
		self.validate_name()
		self.doc.name = self.doc.unit_name
		print self.doc.name
		
	def validate(self):
		self.doc.unit_title = self.doc.unit_title.title()
		self.remove_no_rules_with_no_perms()
		self.make_private_if_parent_is_private()
	
	def on_update(self):
		DocTypeNestedSet.on_update(self)
		clear_unit_views(self.doc.name)
	
	def after_insert(self):
		if self.doc.parent_unit:
			clear_unit_views(self.doc.parent_unit)
		
	def make_private_if_parent_is_private(self):
		if self.doc.parent_unit and not webnotes.conn.get_value("Unit", self.doc.parent_unit, "public_read"):
			self.doc.public_read = 0
	
	def validate_name(self):
		self.doc.unit_name = self.doc.unit_name.strip().lower().replace(" ", "-")
		if re.findall("[^a-zA-Z0-9-]", self.doc.unit_name):
			raise webnotes.ValidationError
	
	def remove_no_rules_with_no_perms(self):
		to_remove = []
		for i, d in enumerate(self.doclist.get({"doctype":"Unit Profile"})):
			if not (d.read or d.write or d.admin):
				to_remove.append(d)
				
		for d in to_remove:
			self.doclist.remove(d)
			
