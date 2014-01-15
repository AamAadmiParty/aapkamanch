# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import webnotes
from webnotes.utils import today, add_days, getdate, get_datetime
from webnotes.utils.email_lib.bulk import send

from .helpers import get_access

def send_daily_summary(for_date=None, event_date=None):
	if not for_date:
		for_date = add_days(today(), days=-1)
	if not event_date:
		event_date = today()
	
	formatted_date = getdate(for_date).strftime("%a, %d %B, %Y")
	formatted_event_date = getdate(event_date).strftime("%a, %d %B, %Y")
	subject = "[AAP Ka Manch] Updates for {formatted_date}".format(formatted_date=formatted_date)
	unit_post_map = get_unit_post_map(for_date, event_date)
	
	if not unit_post_map:
		# no updates!
		return
		
	for user in webnotes.conn.sql_list("""select name from `tabProfile`
		where user_type='Website User' and enabled=1 and name not in ('Administrator', 'Guest')"""):
		
		summary = prepare_daily_summary(user, unit_post_map, {"subject": subject, "formatted_date": formatted_date,
			"formatted_event_date": formatted_event_date})
		
		if not summary:
			# no access!
			continue
		
		send(recipients=[user], 
			subject=subject, 
			message=summary,
		
			# to allow unsubscribe
			doctype='Profile', 
			email_field='name', 
			
			# for tracking sent status
			ref_doctype="Profile", ref_docname=user)
		
	
def prepare_daily_summary(user, unit_post_map, render_opts=None):
	allowed_units = []
	event_post_map = {
		"posts": [],
		"lft": 0,
		"unit_title": "Events on {}".format(render_opts.get("formatted_event_date")),
		"public": 1
	}
	
	for unit in sorted(unit_post_map, key=lambda u: unit_post_map.get(u, {}).get("lft")):
		if get_access(unit, profile=user).get("read"):
			allowed_units.append(unit)
			event_post_map["posts"] += unit_post_map[unit].get("events") or []
			
	if event_post_map["posts"]:
		allowed_units = ["Events"] + allowed_units
			
	if allowed_units:
		if not render_opts: render_opts = {}
		
		render_opts.update({
			"allowed_units": allowed_units,
			"unit_post_map": unit_post_map,
			"event_post_map": event_post_map
		})
		
		return webnotes.get_template("templates/emails/daily_summary.html").render(render_opts)
	else:
		return ""
	
def get_unit_post_map(for_date, event_date):
	"""get a dict of posts per unit and unit properties"""
	unit_post_map = webnotes._dict()
	profiles = {}

	# set posts
	posts = webnotes.conn.sql("""select unit, name, owner, creation,
		content, picture_url, event_datetime,
		(select count(pc.name) from `tabPost` pc where pc.parent_post=p.name) as post_reply_count
		from `tabPost` p where date(creation)=%s and ifnull(parent_post, '')=''
		order by unit, creation""", (for_date,), as_dict=True)
		
	set_posts_in(unit_post_map, posts, "posts", profiles)
	
	# set events
	events = webnotes.conn.sql("""select unit, name, owner, creation,
		content, picture_url, event_datetime,
		(select count(pc.name) from `tabPost` pc where pc.parent_post=p.name) as post_reply_count
		from `tabPost` p where date(event_datetime)=%s and ifnull(parent_post, '')=''
		order by unit, event_datetime""", (event_date,), as_dict=True)

	set_posts_in(unit_post_map, events, "events", profiles)
	
	# update unit info
	for unit, opts in unit_post_map.items():
		opts.update(webnotes.conn.get_value("Unit", opts.unit or unit, 
			["lft", "rgt", "public", "unit_title"], as_dict=True) or {})
		opts.parents = webnotes.conn.sql("""select name, unit_title from tabUnit 
			where lft < %s and rgt > %s order by lft asc""", (opts.lft, opts.rgt), as_dict=1)
		
	return unit_post_map
	
def set_posts_in(unit_post_map, posts, key, profiles):
	for post in posts:
		if not profiles.get(post.owner):
			profiles[post.owner] = webnotes.conn.get_value("Profile", post.owner, 
				["first_name", "last_name", "user_image"], as_dict=True)
		
		post.update(profiles.get(post.owner) or {})
		
		if post.event_datetime:
			post.event_datetime = get_datetime(post.event_datetime)
			post.event_display = post.event_datetime.strftime("%a, %d %B, %Y at %I:%M %p") if key=="posts" \
				else post.event_datetime.strftime("at %I:%M %p")
		
		unit_post_map.setdefault(post.unit, webnotes._dict()).setdefault(key, []).append(post)
	