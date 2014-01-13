# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes

from aapkamanch.helpers import get_access

class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
		
	def validate(self):
		if self.doc.is_task:
			if not self.doc.status:
				self.doc.status = "Open"
		else:
			self.doc.assigned_to = self.doc.status = None
		
	
	def on_update(self):
		webnotes.cache().delete_value("unit_html:" + self.doc.unit)