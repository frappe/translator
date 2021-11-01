// Copyright (c) 2021, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Translator App', {
	refresh: function(frm) {
		frm.add_custom_button(__('Schedule String Extraction Job'), function () {
			frm.call({
				method: "extract_strings_from_app",
				args: { app_name: frm.doc.name },
			}).then(() => {
				frappe.show_alert({
					message:__('"String Extraction Job scheduled successfully'),
					indicator:'green'
				}, 5);
			});
		});
	}
});
