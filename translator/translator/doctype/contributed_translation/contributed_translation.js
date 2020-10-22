// Copyright (c) 2019, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contributed Translation', {
	refresh: function(frm) {
		if (frm.doc.status == 'Contributed') {
			frm.add_custom_button(__('Verify'), () => {
				frm.set_value('status', 'Verified')
				frm.save()
			})
			frm.add_custom_button(__('Reject'), () => {
				frm.set_value('status', 'Rejected')
				frm.save()
			})
		}

	}
});
