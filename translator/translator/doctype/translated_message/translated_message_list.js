frappe.listview_settings['Translated Message'] = {
	hide_name_column: true,
	add_fields: ['translation_source', 'contribution_status'],
	onload: function() {
		if (!frappe.route_options) {
			frappe.route_options = {
				"translation_source": "Community Contribution",
			};
		}
	},

	button: {
		show: function(doc) {
			return doc.contribution_status === 'Pending';
		},
		get_label: function() {
			return __('Verify');
		},
		get_description: function(doc) {
			return __('Verify Contributed Translation')
		},
		action: function(doc) {
			frappe.db.set_value('Translated Message', doc.name, 'contribution_status', 'Verified', () => {
				frappe.show_alert({
					message: __('{0} has been verified.', [(doc.translated).bold()]),
					indicator: 'green'
				})
				cur_list.refresh()
			})
		}
	}
}