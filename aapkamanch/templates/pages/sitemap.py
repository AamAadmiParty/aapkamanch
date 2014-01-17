import webnotes

def get_context():
	return {
		"links": webnotes.conn.sql("""select name as loc, DATE_FORMAT(modified, '%Y-%m-%d') as lastmod
				from tabUnit where ifnull(`public_read`,0)=1""", as_dict=True)
	}