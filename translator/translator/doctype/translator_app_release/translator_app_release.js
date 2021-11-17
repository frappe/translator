// Copyright (c) 2021, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Translator App Release', {
	refresh: function(frm) {
		frm.add_custom_button(__('Schedule String Extraction Job'), function () {
			frm.call({
				method: "create_release_job",
				args: { release: frm.doc.name },
			}).then(() => {
				frappe.show_alert({
					message:__('Release Job scheduled successfully. A new release file will be attached to this document soon.'),
					indicator:'green'
				}, 5);
			});
		});
	}
});
