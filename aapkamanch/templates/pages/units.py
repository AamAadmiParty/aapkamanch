import webnotes

@webnotes.whitelist()
def get_context():
	def get_unit(unit_name):
		unitdoc = webnotes.doc("Unit", unit_name)
		unit = webnotes._dict({
			"unit_name": unit_name,
			"parent_unit": unitdoc.parent_unit,
			"unit_type": unitdoc.unit_type,
			"children_name": unitdoc.children_name,
			"children": []
		})
		for child_unit in webnotes.conn.sql_list("""select name from tabUnit 
			where parent_unit=%s""", unit_name):
			unit.children.append(get_unit(child_unit))
			
		return unit

	return {
		"all_units": get_unit("India")
	}