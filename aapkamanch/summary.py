# Aap Ka Manch, license GNU General Public Licence

from __future__ import unicode_literals

import os
import frappe
from frappe.utils import today, add_days, getdate, get_datetime
from frappe.utils.email_lib.bulk import send
from frappe.website.permissions import get_access
from frappe.templates.generators.website_group import get_pathname

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
		
	for user in frappe.conn.sql_list("""select name from `tabProfile`
		where user_type='Website User' and enabled=1 
		and name not in ('Administrator', 'Guest')"""):
		
		summary = prepare_daily_summary(user, posts, events, {
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
	"""get a dict of posts per group and group properties"""
	# get public posts
	posts = frappe.conn.sql("""select *,
		(select count(pc.name) from `tabPost` pc where pc.parent_post=p.name) as post_reply_count
		from `tabPost` p
		where date(creation)=%s and ifnull(parent_post, '')='' and
		exists(select name from `tabWebsite Group` u where u.name=p.website_group and u.public_read=1)
		order by (p.upvotes + post_reply_count - (timestampdiff(hour, p.creation, %s) / 2)) desc, p.creation desc
		limit 20""",
		(for_date, for_date), as_dict=True)
	
	if posts:
		process_posts(posts)
	
	# get all events, later filtered by access
	events = frappe.conn.sql("""select *,
		(select count(pc.name) from `tabPost` pc where pc.parent_post=p.name) as post_reply_count
		from `tabPost` p where is_event=1 and date(event_datetime)=%s and ifnull(parent_post, '')=''
		order by event_datetime, website_group""", (event_date,), as_dict=True)
	
	if events:
		process_posts(events, is_event=True)
	
	return posts, events

def process_posts(posts, is_event=False):
	if not hasattr(frappe.local, "summary_commons"):
		frappe.local.summary_commons = frappe._dict({
			"website_group": {},
			"profile": {}
		})
		
	summary_commons = frappe.local.summary_commons
		
	for post in posts:
		# profile data
		if not summary_commons.profile.get(post.owner):
			summary_commons.profile[post.owner] = frappe.conn.get_value("Profile", post.owner, 
				["first_name", "last_name", "user_image"], as_dict=True)
				
		post.update(summary_commons.profile.get(post.owner) or {})
		
		# group data
		if not summary_commons.website_group.get(post.website_group):
			opts = frappe.conn.get_value("Website Group", post.website_group, ["group_title", "group_type"], 
				as_dict=True) or {}
			opts.update(frappe.conn.get_value("Website Sitemap", {"ref_doctype": "Website Group",
				"docname": post.website_group}, ["name", "lft", "rgt"], as_dict=True) or {})

			opts["pathname"] = opts["name"]
			del opts["name"]
				
			opts["parents"] = frappe.conn.sql("""select name, page_title as group_title from `tabWebsite Sitemap`
					where lft < %s and rgt > %s order by lft asc""", (opts.lft, opts.rgt), as_dict=True)
			summary_commons.website_group[post.website_group] = opts
		
		post.update(summary_commons.website_group.get(post.website_group) or {})
		
		# event data
		if post.event_datetime:
			post.event_datetime = get_datetime(post.event_datetime)
			post.event_display = post.event_datetime.strftime("%a, %d %B, %Y at %I:%M %p") if not is_event \
				else post.event_datetime.strftime("at %I:%M %p")
				
def get_allowed_events(user, events):
	group_access = {}
	for pathname in set([p.pathname for p in events]):
		group_access[pathname] = get_access(pathname, profile=user).get("read") or 0
	
	allowed_events = []
	for post in events:
		if group_access.get(post.pathname):
			allowed_events.append(post)
			
	return allowed_events
				
daily_summary_template = None
def get_summary_template():
	global daily_summary_template
	
	if not daily_summary_template:
		daily_summary_template = frappe.get_template("templates/emails/daily_summary.html")

	return daily_summary_template
