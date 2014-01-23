# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes
from webnotes.utils import now_datetime
from aapkamanch.helpers import get_access

def get_unit_html(context):
	context["event_list_html"] = get_event_list_html(context.get("name"), view=context.get("view"))

@webnotes.whitelist(allow_guest=True)
def get_event_list_html(unit, view=None, limit_start=0, limit_length=20):
	access = get_access(unit)
	if webnotes.local.form_dict.cmd=="get_event_list_html":
		# for paging
		if not access.get("read"):
			raise webnotes.PermissionError
			
	if view=="upcoming":
		condition = "and p.event_datetime >= %s"
		order_by = "p.event_datetime asc"
	else:
		condition = "and p.event_datetime < %s"
		order_by = "p.event_datetime desc"
	
	# should show based on time upto precision of hour
	# because the current hour should also be in upcoming
	now = now_datetime().replace(minute=0, second=0, microsecond=0)
	
	posts = webnotes.conn.sql("""select p.*, pr.user_image, pr.first_name, pr.last_name,
		(select count(pc.name) from `tabPost` pc where pc.parent_post=p.name) as post_reply_count
		from tabPost p, tabProfile pr
		where p.unit=%s and pr.name = p.owner and ifnull(p.parent_post, '')='' 
			and p.is_event=1 {condition}
		order by {order_by} limit %s, %s""".format(condition=condition, order_by=order_by), 
		(unit, now, int(limit_start), int(limit_length)), as_dict=True)
			
	return webnotes.get_template("templates/includes/post_list.html")\
		.render({"posts": posts, "limit_start":limit_start, "write": access.get("write")})
