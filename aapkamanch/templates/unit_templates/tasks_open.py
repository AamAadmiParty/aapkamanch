# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes
from aapkamanch.helpers import get_access

def get_unit_html(context):
	context["task_list_html"] = get_task_list_html(context.get("name"), view=context.get("view"))

@webnotes.whitelist(allow_guest=True)
def get_task_list_html(unit, view=None, limit_start=0, limit_length=20, status="Open"):
	access = get_access(unit)
	if webnotes.local.form_dict.cmd=="get_task_list_html":
		# for paging
		if not access.get("read"):
			raise webnotes.PermissionError
	
	posts = webnotes.conn.sql("""select p.*, pr.user_image, pr.first_name, pr.last_name,
		(select count(pc.name) from `tabPost` pc where pc.parent_post=p.name) as post_reply_count
		from tabPost p, tabProfile pr
		where p.unit=%s and pr.name = p.owner and ifnull(p.parent_post, '')='' 
			and p.is_task=1 and p.status = %s
		order by p.creation desc limit %s, %s""", 
		(unit, status, int(limit_start), int(limit_length)), as_dict=True)
			
	return webnotes.get_template("templates/includes/post_list.html")\
		.render({"posts": posts, "limit_start":limit_start, "write": access.get("write")})