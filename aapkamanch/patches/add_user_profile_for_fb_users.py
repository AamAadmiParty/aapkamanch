import webnotes

def execute():
	webnotes.conn.sql("""update tabProfile set 
		user_image = concat('https://graph.facebook.com/', fb_username, '/picture')
		where ifnull(fb_username, '') != '' """)