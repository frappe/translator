$(document).ready(function() {
	$("body").on("click", ".translated", function(e) {
		translator.activate($(this));
	});

	$("body").on("click", ".btn-verify", function() {
		translator.verify($(this));
	});
});

function getNextRow($row) {
	$row = $row.next()
	if ($row.find("button.btn-verify[data-verified=0]").size() > 0) {
		console.log($row.find("button.btn-verify[data-verified=0]").size())
		return $row
	}
	return getNextRow($row)
}

function getNextTranslation($currentElement) {
	$row = getNextRow($currentElement.closest('.row'))
	return $row.find('.translated')
}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

frappe.ready(function() {
	if(location.pathname=="/translator/view") {
		$(".page-header h2").html("Translate " + window.language_name);
		document.title = "Translate " + window.language_name;
		$("[data-char='"+(get_url_arg("c") || "*")+"']").addClass("active");
	}

	$(".message-ts").each(function() {
		var ts = $(this).attr("data-timestamp");
		$(this).html("Last Updated: "
		 + (comment_when(ts) || ts));
	});

	$("input#search-box").keyup(function(event){
		if(event.keyCode == 13){
			search_param = $(this).val()
			lang = getParameterByName('lang')
			if (search_param && lang) {
				window.location = "/translator/view?lang="+lang+"&search="+search_param
			}
		}
	});

});


var translator = {
	remove: function(cancel) {
		var $txt = $(".edit-value"),
			val = $txt.val();

		if(!$txt.length) {
			return;
		}

		if(cancel || val===$txt.attr('data-original')) {
			var $next = getNextTranslation($txt)
			$txt.parent().removeClass("active").html($txt.attr('data-original'));
			$next.trigger('click')
			return;
		}

		if(!val) {
			frappe.msgprint("Please enter translated text");
			return;
		}

		frappe.call({
			method: "translator.helpers.update",
			args: {
				message: $txt.parents(".row:first").attr("data-message-id"),
				source: $txt.parents(".row:first").attr("data-source-message-id"),
				language: window.lang,
				translated: val
			},
			callback: function(data) {
				if(!data.exc) {
					$next = getNextTranslation($txt)
					$txt.parent().removeClass("active").html(val);
					$next.trigger('click')
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
			$cancel = $('<button class="btn btn-default btn-small">Next</button>')
				.appendTo($p)
				.on("click", function(e) {
					translator.remove(true);
				});
			$update = $('<button class="btn btn-primary btn-small">Update</button>')
				.appendTo($p)
				.css({"margin-left": "5px"})
				.on("click", function() {
					translator.remove();
				}),

			// report
			$p1 = $('<p style="margin-top: 5px;"></p>').appendTo($me),
			$check = $('<div class="checkbox">\
				<label class="text-muted"><input type="checkbox"> This message is badly framed in English.</label></div>')
				.appendTo($p1)
				.change(function() {
					translator.report($(this).parents(".row:first"), $(this).prop("checked"));
				});


		if(window.lang=="ar") {
			$txt.addClass('text-right');
		}

	},
	verify: function($btn) {
		frappe.call({
			method: "translator.helpers.verify",
			args: {
				message: $btn.parents(".row:first").attr("data-message-id")
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

	},
	report: function($row, value) {
		frappe.call({
			method: "translator.helpers.report",
			args: {
				message: $row.attr("data-source-message-id"),
				value: value ? 1 : 0,
			},
			callback: function(data) {
				if(!data.exc) {
					$row.find(".icon-flag").toggleClass("hide", value);
				}
			}
		});
	}
}

