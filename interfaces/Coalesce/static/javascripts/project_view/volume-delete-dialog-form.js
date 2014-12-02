$(function() {

	var message = new message_handle();	// Initializes message handling

	// Hide delete-volume button when page initializes with no instances
	if($('#volume-placeholder').length) {
		if ($('#delete-volume').is(':visible')) { $('#delete-volume').toggle(); }
	}

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

		var volume = $( "#volume" );

		$( "#volume-delete-dialog-form" ).dialog({
			autoOpen: false,
			height: 250,
			width: 350,
			modal: true,
			buttons: {
				"Confirm": function() {

					message.showMessage('notice', 'Deleting Volume');	// Flag notice

                    if ($('#create-volume').is(':visible')){ $('#delete-instance').toggle(); }
                    if ($('#delete-volume').is(':visible')){ $('#create-instance').toggle(); }

					// Initialize progressbar and make it visible if hidden
					$('#vol_progressbar').progressbar({value: false});
					if ($('#vol_progressbar').is(':hidden')) { $('#vol_progressbar').toggle(); };

					$.getJSON('/delete_volume/' + volume.val() + '/' + PROJECT_ID + '/')
					.success(function(data){

						// Check if instance was successfully deleted
						if(data.status == 'error'){ 						// Flag error message 

							message.showMessage('error', data.message); 

							// Hide progressbar on completion
                        	if ($('#vol_progressbar').is(':visible')) { $('#vol_progressbar').toggle(); };

                        	$('#delete-volume').attr("disabled", false);	// Enable delete-instance button
						}
						
						if(data.status == 'success'){ 						// Update interface

							message.showMessage('success', data.message);	// Flag success message

							// Remove volume row from volume_list
							var targetRow = '#' + volume.val();
							$('#volume_list').find(targetRow).fadeOut().remove();

							// Remove volume from delete-volume select menu
                        	var targetOption = 'select#volume option[value='+volume.val()+']';
                        	$(targetOption).remove();

                        	// Hide progressbar on completion
                        	if ($('#vol_progressbar').is(':visible')) { $('#vol_progressbar').toggle(); }

                            if ($('#create-volume').is(':hidden')){ $('#delete-instance').toggle(); }
                            if ($('#delete-volume').is(':hidden')){ $('#create-instance').toggle(); }

                            // Check to see if this is the last volume, if so add a placeholder row and hide delete-volume button
                            var rowCount = $('#volume_list tr').length;
                            if (rowCount < 2) {
                                var placeholder = '<tr id="volume-placeholder"><td><p><i>This project has no volumes</i></p></td><td></td><td></td>/tr>';
                                $('#volume_list').append(placeholder).fadeIn();
                                if ($('#delete-volume').is(':visible')) {	$('#delete-volume').toggle();	}
                            }
                        }
                    })
					.error(function(){

						message.showMessage('error', 'Server Fault');	// Flag server fault message

						// Hide progressbar on error
						if ($('#vol_progressbar').is(':visible')) { $('#vol_progressbar').toggle(); }
                        if ($('#create-volume').is(':hidden')){ $('#delete-instance').toggle(); }
                        if ($('#delete-volume').is(':hidden')){ $('#create-instance').toggle(); }
					});

					$( this ).dialog( "close" );	// Close modal form	
				},
				Cancel: function() {
					$( this ).dialog( "close" );
				}
			},
			close: function() { }
		})

		$( "#delete-volume" ).click(function() { $( "#volume-delete-dialog-form" ).dialog( "open" ); });
	});
});
