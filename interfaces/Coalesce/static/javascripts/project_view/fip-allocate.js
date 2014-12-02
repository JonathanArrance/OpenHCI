$(function() {

	var message = new message_handle();	// Initialize message handling

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

		var extNet = $('.allocate_ip').attr("id");

		$(".allocate_ip").click(function() {

            if ($('.allocate_ip').is(':visible')){ $('.allocate_ip').toggle(); }
            if ($('#assign_ip').is(':visible')){ $('#assign_ip').toggle(); }

            $('.disable-action').bind('click', false);
            var origActionColor = $('.disable-action').css('color');
            $('.disable-action').css('color', '#696969');

			$.getJSON('/allocate_floating_ip/' + PROJECT_ID + '/' + extNet + '/')
			.success(function(data) {

				// Check if instance was successfully generated
				if(data.status == 'error'){ message.showMessage('error', data.message); };	// Flag error message
				if(data.status == 'success'){												// Update interface
					message.showMessage('success', "Successfully allocated "+data.ip_info.floating_ip+".");	// Flag notice

					// --- BEGIN html string generation
					// Initialize empty string for new instance row
					var newRow = '';
					// Start row
					newRow += '<tr id="'+data.ip_info.floating_ip+'">';
					// Create ip-cell
					newRow += '<td id="'+data.ip_info.floating_ip+'-ip-cell"><a href="/floating_ip/'+data.ip_info.floating_ip_id+'/view/" class="disable-action"><span id="'+data.ip_info.floating_ip+'-ip-address">'+data.ip_info.floating_ip+'</span></a></td>';
					// Create instance-cell
					newRow += '<td id="'+data.ip_info.floating_ip+'-instance-cell"><span id="'+data.ip_info.floating_ip+'-instance-name">None</span></td>';
					// Create actions-cell
					newRow += '<td id="'+data.ip_info.floating_ip+'-actions-cell"><a id="'+data.ip_info.floating_ip+'" class="deallocate_ip" href="#">deallocate</a></td>';
					// End row
					newRow += '</tr>';
					// --- END html string generation

                    // Check to see if this is the first fip to be generated, if so remove placeholder and reveal assign_ip button
                    var rowCount = $('#fip_list tr').length;
                    if (rowCount <= 2) {
                        $('#fip_placeholder').remove().fadeOut();
                        if ($('#assign_ip').is(':hidden')){ $('#assign_ip').toggle(); }
                    }

					// Append new row to instance-list
					$('#fip_list').append(newRow).fadeIn();

					var newOption = '<option value="'+data.ip_info.floating_ip+'">'+data.ip_info.floating_ip+'</option>';
				   	$('div#fip-assign-dialog-form > form > fieldset > select#assign_floating_ip').append(newOption);
				}

                if ($('.allocate_ip').is(':hidden')){ $('.allocate_ip').toggle(); }
                if ($('#assign_ip').is(':hidden')){ $('#assign_ip').toggle(); }

                $('.disable-action').unbind('click', false);
                $('.disable-action').css('color', origActionColor);

			})
			.error(function(){
				message.showMessage('error', 'Server Fault');

                if ($('.allocate_ip').is(':hidden')){ $('.allocate_ip').toggle(); }
                if ($('#assign_ip').is(':hidden')){ $('#assign_ip').toggle(); }

                $('.disable-action').unbind('click', false);
                $('.disable-action').css('color', origActionColor);
			});
		});
	});
});

$(document).ready(function() {
    var rowCount = $('#fip_list tr').length;
    if (rowCount <= 2) { if ($('#assign_ip').is(':visible')){ $('#assign_ip').toggle(); }}
});