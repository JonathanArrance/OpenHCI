$(function() {  

	var message = new message_handle();	// Initialize message handling

	// Hide delete-instance button when page initializes with no instances
	if ($('#instance_placeholder').length) {	
		if ($('#delete-instance').is(':visible')) {	$('#delete-instance').toggle(); }; 
	};

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

		var instance = $('#instance'),
			tips = $( ".validateTips" );

		function updateTips( t ) {
			tips.text( t ).addClass( "ui-state-highlight" );
			setTimeout(function() { tips.removeClass( "ui-state-highlight", 1500 ); }, 500 );
		}

		$( "#instance-delete-dialog-form" ).dialog({
			autoOpen: false,
			height: 250,
			width: 350,
			modal: true,
			buttons: {
				"Confirm": function() {

					message.showMessage('notice', 'Deleting Instance');	// Flag notice

					$('#delete-instance').attr("disabled", true);		// Disable delete-instance button					
					$('#create-instance').attr("disabled", true);		// Disable delete-instance button

					// Initialize progressbar and make it visible if hidden
					$('#instance_progressbar').progressbar({value: false});
					if ($('#instance_progressbar').is(':hidden')) {	$('#instance_progressbar').toggle(); };

					$.getJSON('/server/' + PROJECT_ID + '/' + instance.val() + '/delete_server/')
						.success(function(data){

							// Check if instance was successfully deleted
                        	if(data.status == 'error'){ message.showMessage('error', data.message); }; 	// Flag error message 
                        	if(data.status == 'success'){ 												// Update interface

                        		message.showMessage('success', data.message);	// Flag success message

                        		// Remove instance row from instance_list
                        		var targetRow = '#' + instance.val();
                        		$('#instance_list').find(targetRow).fadeOut().remove();

                        		// Remove instance from delete-instance select menu
                        		var targetOption = 'select#instance option[value='+instance.val()+']';
                        		$(targetOption).remove();

                        		// Check to see if this is the last instance, if so add a placeholder row and hide delete-instance button
                        		var rowCount = $('#instance_list tr').length;
                        		if (rowCount < 2) {
                        			var placeholder = '<tr id="instance_placeholder"><td><p><i>This project has no instances</i></p></td><td></td><td></td><td></td></tr>';
                        			$('#instance_list').append(placeholder).fadeIn();
                        			if ($('#delete-instance').is(':visible')) {	$('#delete-instance').toggle();	};
                        		};

                        		// Hide progressbar on completion
                        		if ($('#instance_progressbar').is(':visible')) { $('#instance_progressbar').toggle(); };

                        		$('#delete-instance').attr("disabled", false);	// Enable delete-instance button
                        		$('#create-instance').attr("disabled", false);	// Enable create-instance button
                        	};
                        })
						.error(function(){

							message.showMessage('error', 'Server Fault');	// Flag server fault message

							// Hide progressbar on error
							if ($('#instance_progressbar').is(':visible')) { $('#instance_progressbar').toggle(); };

							$('#delete-instance').attr("disabled", false);	// Enable delete-instance button
							$('#create-instance').attr("disabled", false);	// Enable create-instance button
						});

					$( this ).dialog( "close" );	// Close modal form	
				},
				Cancel: function() { $( this ).dialog( "close" ); }	// Close modal form				
			},
			close: function() {	}
		})

		// Open modal form when delete-instance button clicked
		$( "#delete-instance" ).click(function() { $( "#instance-delete-dialog-form" ).dialog( "open" ); });
	});
});
