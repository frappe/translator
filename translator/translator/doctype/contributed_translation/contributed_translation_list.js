frappe.listview_settings['Contributed Translation'] = {
	hide_name_column: true,
	onload: function() {
		if (!frappe.route_options) {
			frappe.route_options = {
				"status": "Contributed",
				"language": "hi"
			};
		}
	},

	button: {
		show: function(doc) {
			return doc.status === 'Contributed';
		},
		get_label: function() {
			return __('Verify');
		},
		get_description: function(doc) {
			return __('Verify Contributed Translation')
		},
		action: function(doc) {
			frappe.db.set_value('Contributed Translation', doc.name, 'status', 'Verified', () => {
				frappe.show_alert({
					message: __('{0} has been verified.', [(doc.translated_string).bold()]),
					indicator: 'green'
				})
				cur_list.refresh()
			})
		}
	}
}