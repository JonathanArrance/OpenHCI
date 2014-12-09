$(function() {

	var message = new message_handle();	// Initialize message handling
	var fip = '';
	var targetRow; 

	// must obtain csrf cookie for AJAX call
	function getCookie(name) {
		var cookieValue = null;
		if (document.cookie && document.cookie != '') {
			var cookies = document.cookie.split(';');
			for (var i = 0; i < cookies.length; i++) {
				var cookie = jQuery.trim(cookies[i]);

				// Does this cookie string begin with the name we want?
				if (cookie.substring(0, name.length + 1) == (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}

	var csrftoken = getCookie('csrftoken');

	$(function() {

		function csrfSafeMethod(method) {
			// these HTTP methods do not require CSRF protection
			return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
		}

		$.ajaxSetup({
			crossDomain: false, // obviates need for sameOrigin test
			beforeSend: function(xhr, settings) {
				if (!csrfSafeMethod(settings.type)) {
					xhr.setRequestHeader("X-CSRFToken", csrftoken);
				}
			}
		});

		var tips = $( ".validateTips" );

		function updateTips( t ) {
			tips.text( t ).addClass( "ui-state-highlight" );
			setTimeout(function() { tips.removeClass( "ui-state-highlight", 1500 ); }, 500 );
		}

		$('#fip-deallocate-confirm-form').dialog({
			autoOpen: false,
			height: 150,
			width: 350,
			modal: true,
			buttons: {
				"Confirm": function() {

					var confirmedFip = fip;
					message.showMessage('notice', "Deallocating "+confirmedFip+".");

                    if ($('.allocate_ip').is(':visible')){ $('.allocate_ip').toggle(); }
                    if ($('#assign_ip').is(':visible')){ $('#assign_ip').toggle(); }

					$.getJSON('/deallocate_floating_ip/' + PROJECT_ID + '/' + confirmedFip + '/')
					.success(function(data) {

						// Check if instance was successfully generated
						if(data.status == 'error'){ message.showMessage('error', data.message); };	// Flag error message
						if(data.status == 'success'){												// Update interface
							message.showMessage('success', data.message);	// Flag notice

							//var targetRow = 'tr#'+fip;
							$(targetRow).fadeOut().remove();

							var targetOption = 'select#assign_floating_ip option[value="'+confirmedFip+'"]';
				   			$(targetOption).remove();
						}

                        if ($('.allocate_ip').is(':hidden')){ $('.allocate_ip').toggle(); }
                        if ($('#assign_ip').is(':hidden')){ $('#assign_ip').toggle(); }

                        // Check to see if this is the last fip to be deallocated, if so reveal placeholder and hide assign_ip button
                        var placeholder = ''
                        var rowCount = $('#fip_list tr').length;
                        if (rowCount < 2) {
                            var placeholder = '<tr id="fip_placeholder"><td><p><i>This project has no floating IPs</i></p></td><td></td><td></td></tr>';
                            $('#fip_list').append(placeholder).fadeIn();
                            if ($('#assign_ip').is(':visible')) {
                                $('#assign_ip').toggle();
                            }
                        }
                    })
					.error(function(){
						message.showMessage('error', 'Server Fault');

                        if ($('.allocate_ip').is(':hidden')){ $('.allocate_ip').toggle(); }
                        if ($('#assign_ip').is(':hidden')){ $('#assign_ip').toggle(); }
					});

					$( this ).dialog( "close" );
				},

				Cancel: function() { $( this ).dialog( "close" ); }
			}
		});

		$(document).on('click', '.deallocate_ip', function(){

			targetRow = $(this).parent().parent();
			fip = $(this).attr("id");
			
			$('div#fip-deallocate-confirm-form > p > span.ip-address')
				.empty()
				.append(fip);

			$('#fip-deallocate-confirm-form').dialog("open");
		});
	});
});