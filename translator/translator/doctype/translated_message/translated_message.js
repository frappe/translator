// Copyright (c) 2020, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Translated Message', {
	refresh: function(frm) {
		if (frm.doc.contribution_status == 'Pending') {
			frm.add_custom_button(__('Verify'), () => {
				frm.set_value('contribution_status', 'Verified')
				frm.save()
			})
			frm.add_custom_button(__('Reject'), () => {
				frm.set_value('contribution_status', 'Rejected')
				frm.save()
			})
		}

	}
});