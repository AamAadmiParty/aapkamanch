# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals
import webnotes

no_cache = 1

def get_context():
	tasks = get_task_list()
	
	return {
		"show_back_btn": True,
		"title": "Tasks",
		"post_list_html": get_task_list_html(tasks=tasks),
		"public": 1,
		"parents": [{"name": "", "unit_title": "Home"}]
	}

def get_task_list(limit_start=0, limit_length=20):
	return webnotes.conn.sql("""select p.name, p.unit, p.is_task,
		p.creation, p.content, pr.fb_username, pr.first_name, pr.last_name,
		p.assigned_to, p.event_datetime, p.assigned_to_fullname, p.parent_post,
		(select count(pc.name) from `tabPost` pc where pc.parent_post=p.name) as post_reply_count
		from tabPost p, tabProfile pr
		where p.assigned_to=%s and pr.name = p.owner and ifnull(p.status, '')!='Completed'
		order by p.creation desc limit %s, %s""", 
		(webnotes.session.user, limit_start, limit_length), as_dict=True)
			
def get_unit_map(tasks):
	units = [t.unit for t in tasks]
	return webnotes.conn.get_value_for_many_names("Unit", units, "public")

@webnotes.whitelist()
def get_task_list_html(tasks=None, limit_start=0, limit_length=20):
	if not tasks:
		tasks = get_task_list(limit_start, limit_length)
	
	unit_map = get_unit_map(tasks)
	for post in tasks:
		post["public"] = unit_map.get(post.unit)
			
	return webnotes.get_template("templates/includes/post_list.html").render({
		"posts": tasks, 
		"limit_start":limit_start, 
		"with_unit": True, 
		"write": 1
	})