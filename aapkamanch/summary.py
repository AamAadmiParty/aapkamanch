# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import os
from inlinestyler.utils import inline_css

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
	posts, events = get_posts_and_events(for_date, event_date)
	
	if not (posts or events):
		# no updates!
		return
		
	for user in webnotes.conn.sql_list("""select name from `tabProfile`
		where user_type='Website User' and enabled=1 and name not in ('Administrator', 'Guest')"""):
		
		summary = prepare_daily_summary(user, posts, events, {
			"subject": subject, 
			"formatted_date": formatted_date, 
			"formatted_event_date": formatted_event_date
		})
		
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
		
def prepare_daily_summary(user, posts, events, render_opts=None):
	# show events based on access
	allowed_events = get_allowed_events(user, events)
	
	if not (posts or allowed_events):
		return ""
		
	if not render_opts: render_opts = {}
	
	render_opts.update({
		"posts": posts,
		"events": allowed_events
	})
	
	return get_summary_template().render(render_opts)
	
def get_posts_and_events(for_date, event_date):
	"""get a dict of posts per unit and unit properties"""
	# get public posts
	posts = webnotes.conn.sql("""select *,
		(select count(pc.name) from `tabPost` pc where pc.parent_post=p.name) as post_reply_count
		from `tabPost` p
		where date(creation)=%s and ifnull(parent_post, '')='' and
		exists(select name from `tabUnit` u where u.name=p.unit and u.public_read=1)
		order by (p.upvotes + post_reply_count - (timestampdiff(hour, p.creation, %s) / 2)) desc, p.creation desc
		limit 20""",
		(for_date, for_date), as_dict=True)
	
	if posts:
		process_posts(posts)
	
	# get all events, later filtered by access
	events = webnotes.conn.sql("""select *,
		(select count(pc.name) from `tabPost` pc where pc.parent_post=p.name) as post_reply_count
		from `tabPost` p where is_event=1 and date(event_datetime)=%s and ifnull(parent_post, '')=''
		order by event_datetime, unit""", (event_date,), as_dict=True)
	
	if events:
		process_posts(events, is_event=True)
	
	return posts, events

def process_posts(posts, is_event=False):
	if not hasattr(webnotes.local, "summary_commons"):
		webnotes.local.summary_commons = webnotes._dict({
			"unit": {},
			"profile": {}
		})
		
	summary_commons = webnotes.local.summary_commons
		
	for post in posts:
		# profile data
		if not summary_commons.profile.get(post.owner):
			summary_commons.profile[post.owner] = webnotes.conn.get_value("Profile", post.owner, 
				["first_name", "last_name", "user_image"], as_dict=True)
				
		post.update(summary_commons.profile.get(post.owner) or {})
		
		# unit data
		if not summary_commons.unit.get(post.unit):
			opts = webnotes.conn.get_value("Unit", post.unit, ["lft", "rgt", "unit_title", "unit_type"], 
				as_dict=True) or {}
			opts["parents"] = webnotes.conn.sql("""select name, unit_title from tabUnit 
				where lft < %s and rgt > %s order by lft asc""", (opts.lft, opts.rgt), as_dict=True)
			summary_commons.unit[post.unit] = opts
		
		post.update(summary_commons.unit.get(post.unit) or {})
		
		# event data
		if post.event_datetime:
			post.event_datetime = get_datetime(post.event_datetime)
			post.event_display = post.event_datetime.strftime("%a, %d %B, %Y at %I:%M %p") if not is_event \
				else post.event_datetime.strftime("at %I:%M %p")
				
def get_allowed_events(user, events):
	unit_access = {}
	for unit in set([p.unit for p in events]):
		unit_access[unit] = get_access(unit, profile=user).get("read") or 0
	
	allowed_events = []
	for post in events:
		if unit_access.get(post.unit):
			allowed_events.append(post)
			
	return allowed_events
				
daily_summary_template = None
def get_summary_template():
	global daily_summary_template
	
	if not daily_summary_template:
		# load template
		jenv = webnotes.get_jenv()
		template_path = os.path.join(os.path.dirname(__file__), "templates", "emails", "daily_summary.html")
		with open(template_path, "r") as t:
			daily_summary_template = jenv.from_string(inline_css(t.read()))
	
	return daily_summary_template
