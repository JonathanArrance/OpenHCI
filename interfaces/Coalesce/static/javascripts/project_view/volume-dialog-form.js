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
		
		var volume_name = $( "#volume_name" ),
			volume_size = $( "#volume_size" ),
			description = $( "#description" ),
			volume_type = $( "#volume_type" ),
			allFields = $( [] ).add( volume_name ).add( volume_size ).add( description ).add( volume_type ),
			tips = $( ".validateTips" );

		function updateTips( t ) {
			tips.text( t ).addClass( "ui-state-highlight" );
			setTimeout(function() { tips.removeClass( "ui-state-highlight", 1500 ); }, 500 );
		}

		function checkLength( o, n, min, max ) {
			if ( o.val().length > max || o.val().length < min ) {
				o.addClass( "ui-state-error" );
				updateTips( "Length of " + n + " must be between " +
					min + " and " + max + "." );
				return false;
			} else {
				return true;
			}
		}

		$( "#volume-dialog-form" ).dialog({
			autoOpen: false,
			height: 450,
			width: 350,
			modal: true,
			buttons: {
				"Create a volume": function() {

					var bValid = true;
					allFields.removeClass( "ui-state-error" ); // Remove UI validation flags

					bValid = bValid && checkLength( volume_name, "volume_name", 3, 16 ); // Validate volume_name length
					
					// If volume parameters are valid, proceed with volume generation
					if ( bValid ) {

						message.showMessage('notice', 'Creating new volume '+volume_name.val());	// Flag notice

						$('#create-volume').attr("disabled", true);									// Disable create-volume button

						// Initialize progressbar and make it visible if hidden
						$('#vol_progressbar').progressbar({value: false});
						if ($('#vol_progressbar').is(':hidden')) { $('#vol_progressbar').toggle(); };

					   $.getJSON('/create_volume/' + volume_name.val() + '/' + volume_size.val() + '/' + description.val() + '/' + volume_type.val() + '/' + PROJECT_ID + '/')
					   .success(function(data){

					   		if(data.status == 'error'){message.showMessage('error', data.message);}	// Flag error message
					   		if(data.status == 'success'){											// Flag success message

					   			message.showMessage('success', data.message);	// Flag success message

					   			var newRow = '';								// Initialize empty string for new volume row

					   			// --- BEGIN html string generation
					   			// Start row
					   			newRow += '<tr id="'+data.volume_id+'">';
					   			// Create name-cell
					   			newRow += '<td id="'+data.volume_id+'-name-cell"><a href="/projects/'+PROJECT_ID+'/volumes/'+data.volume_id+'/view/" target="_blank"><span id="'+data.volume_id+'-name-text">'+data.volume_name+'</span></a></td>';
					   			// Create attached-cell
					   			newRow += '<td id="'+data.volume_id+'-attached-cell"><span id="'+data.volume_id+'-attached-placeholder">No Attached Instances</span></td>';
					   			// Create actions-cell
					   			newRow += '<td id="'+data.volume_id+'-actions-cell"><a href="#" class="attach-instance">attach</a></td>';
					   			// End Row
					   			newRow += '</tr>';
					   			// --- END html string generation

					   			// Check to see if this is the first volume to be generated, if so remove placeholder and reveal delete-instance button
					   			var rowCount = $('#volume_list tr').length;
					   			if (rowCount <= 2) {
					   				$('#volume-placeholder').remove().fadeOut();
					   				if ($('#delete-volume').is(':hidden')) { $('#delete-volume').toggle(); };
					   			};

					   			// Append new row to volume-list
					   			$('#volume_list').append(newRow).fadeIn();

					   			// Append new option to delete-volume select menu
					   			var targetSelect = 'div#volume-delete-dialog-form > form > fieldset > select#volume';
					   			var newOption = '<option value ="'+data.volume_id+'">'+data.volume_name+'</option>';
					   			$(targetSelect).append(newOption);
					   		}

					   		// Hide progressbar on completion
							if ($('#vol_progressbar').is(':visible')) { $('#vol_progressbar').toggle(); };

							$('#create-volume').attr("disabled", false);	// Enable create-volume button upon completion
					   	})
					   .error(function(){

					   		message.showMessage('error', 'Server Fault');	// Flag server fault message

					   		// Hide progressbar on completion
							if ($('#vol_progressbar').is(':visible')) { $('#vol_progressbar').toggle(); };

							$('#create-volume').attr("disabled", false);	// Enable create-volume button upon completion
					   	});

					   $( this ).dialog( "close" );
					}
				},
				Cancel: function() {
					$( this ).dialog( "close" );
				}
			},
			close: function() {	allFields.val( "" ).removeClass( "ui-state-error" ); } // Remove ui validations
		})

		// Open modal form when create-volume button is clicked
		$( "#create-volume" ).click(function() { $( "#volume-dialog-form" ).dialog( "open" ); });
	});
});
