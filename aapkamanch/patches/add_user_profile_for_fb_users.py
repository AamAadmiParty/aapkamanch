import frappe

def execute():
	frappe.conn.sql("""update tabProfile set 
		user_image = concat('https://graph.facebook.com/', fb_username, '/picture')
		where ifnull(fb_username, '') != '' """)