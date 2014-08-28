var translator = {
	remove: function(cancel) {
		var $txt = $(".edit-value"),
			val = $txt.val();

		if(!$txt.length) {
			return;
		}

		if(cancel || val===$txt.attr('data-original')) {
			$txt.parent().removeClass("active").html($txt.attr('data-original'));
			return;
		}

		if(!val) {
			frappe.msgprint("Please enter translated text");
			return;
		}

		frappe.call({
			method: "translator.helpers.update",
			args: {
				message: $txt.parent().attr("data-message-id"),
				translated: val
			},
			callback: function(data) {
				if(!data.exc) {
					$txt.parent().removeClass("active").html(val);
				}
			}
		});

	},
	activate: function($div) {
		if(getCookie("sid")==="Guest") {
			frappe.msgprint("Please <a href='/login'>login</a> to edit / verify");
			return;
		}

		if($div.hasClass("active"))
			return;

		var verified = parseInt($div.attr("data-verified"));

		if(verified && window.user_karma < 100) {
			frappe.msgprint("You need 100 karma to edit verified translations.");
			return;
		}

		translator.remove();
		var content = $div.text().trim(),
			$me = $div.empty().addClass("active"),
			$txt = $('<textarea class="edit-value form-control">' + content + '</textarea>')
				.appendTo($me)
				.attr('data-original', content)
				.focus(),
			$p = $('<p class="text-right" style="margin-top: 5px;"></p>').appendTo($me),
			$cancel = $('<button class="btn btn-default btn-small">Cancel</button>')
				.appendTo($p)
				.on("click", function() {
					translator.remove(true);
				});
			$update = $('<button class="btn btn-primary btn-small">Update</button>')
				.appendTo($p)
				.css({"margin-left": "5px"})
				.on("click", function() {
					translator.remove();
				});

	},
	verify: function($btn) {
		frappe.call({
			method: "translator.helpers.verify",
			args: {
				message: $btn.attr("data-message-id")
			},
			callback: function(data) {
				if(!data.exc) {
					var verified = (parseInt($btn.attr("data-verified")) + 1);
					$btn.html("Verified ("+ verified +")");
					if(verified===1) {
						$btn.removeClass("btn-danger").addClass("btn-success");
					}
					$btn.attr("data-verified", verified);
				}
			}
		});

	}
}

$(document).ready(function() {
	$("body").on("click", ".translated", function(e) {
		translator.activate($(this));
	});

	$("body").on("click", ".btn-verify", function() {
		translator.verify($(this));
	});
});

frappe.ready(function() {
	if(location.pathname=="/translator/view") {
		$(".page-header h2").html("Translate " + window.language_name);
		document.title = "Translate " + window.language_name;
		$("[data-char='"+(get_url_arg("c") || "A")+"']").addClass("active");
	}

	$(".message-ts").each(function() {
		$(this).html("Last Updated: " +comment_when($(this).attr("data-timestamp")));
	});
});
