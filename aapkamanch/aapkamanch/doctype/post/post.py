# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals

import webnotes
from webnotes.utils import get_fullname
from webnotes.utils.email_lib.bulk import send
from webnotes.utils.email_lib import sendmail

from aapkamanch.helpers import get_access
from aapkamanch.aapkamanch.doctype.unit.unit import clear_unit_views

class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
		
	def validate(self):
		self.assigned_to = webnotes.conn.get_value(self.doc.doctype, self.doc.name, "assigned_to")
		if self.doc.is_task:
			if not self.doc.status:
				self.doc.status = "Open"
		else:
			self.doc.assigned_to = self.doc.status = None
			
	def on_update(self):
		clear_unit_views(self.doc.unit, "unit_html")

		if self.doc.assigned_to and self.doc.assigned_to != self.assigned_to \
			and webnotes.session.user != self.doc.assigned_to:
			
			# send assignment email
			sendmail(recipients=[self.doc.assigned_to], 
				subject="You have been assigned this Task by {}".format(get_fullname(self.doc.modified_by)),
				msg=self.get_reply_email_message(get_fullname(self.doc.owner)))
		
	def send_email_on_reply(self):
		owner_fullname = get_fullname(self.doc.owner)
		
		parent_post = webnotes.bean("Post", self.doc.parent_post).doc
		
		message = self.get_reply_email_message(owner_fullname)
		
		# send email to the owner of the post, if he/she is different
		if parent_post.owner != self.doc.owner:
			send(recipients=[parent_post.owner], 
				subject="{someone} replied to your post".format(someone=owner_fullname), 
				message=message,
			
				# to allow unsubscribe
				doctype='Profile', 
				email_field='name', 
				
				# for tracking sent status
				ref_doctype=self.doc.doctype, ref_docname=self.doc.name)
		
		# send email to members who part of the conversation
		recipients = webnotes.conn.sql_list("""select owner from `tabPost`
			where parent_post=%s and owner not in (%s, %s)""", 
			(self.doc.parent_post, parent_post.owner, self.doc.owner))
		
		send(recipients=recipients, 
			subject="{someone} replied to a post by {other}".format(someone=owner_fullname, 
				other=get_fullname(parent_post.owner)), 
			message=message,
		
			# to allow unsubscribe
			doctype='Profile', 
			email_field='name', 
			
			# for tracking sent status
			ref_doctype=self.doc.doctype, ref_docname=self.doc.name)
		
	def get_reply_email_message(self, owner_fullname=None):
		message = self.doc.content
		if self.doc.picture_url:
			message += """<div><img src="{url}" style="max-width: 100%"></div>"""\
				.format(url=self.doc.picture_url)
		message += "<p>By {fullname}</p>".format(fullname=owner_fullname)
		return message