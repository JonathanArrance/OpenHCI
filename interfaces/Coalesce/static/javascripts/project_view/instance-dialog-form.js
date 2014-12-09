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

		var sec_group_name = $( "#sec_group_name" ),
			sec_key_name = $( "#sec_key_name" ),
			image_name = $( "#image_name" ),
			name= $( "#name" ),
			network_name = $( "#network_name" ),
			flavor_name = $( "#flavor_name"),
			allFields = $( [] ).add( sec_group_name ).add(sec_key_name).add(image_name).add(name).add(network_name),
			tips = $( ".validateTips" );

		function updateTips( t ) {
			tips.text( t ).addClass( "ui-state-highlight" );
			setTimeout(function() {	tips.removeClass( "ui-state-highlight", 1500 );	}, 500 );
		}

		function checkLength( o, n, min, max ) {
			if ( o.val().length > max || o.val().length < min ) {
				o.addClass( "ui-state-error" );
				updateTips( "Length of " + n + " must be between " + min + " and " + max + "." );
				return false;
			} else {
				return true;
			}
		}

		$( "#instance-dialog-form" ).dialog({
			autoOpen: false,
			height: 550,
			width: 350,
			modal: true,
			buttons: {
				"Create an instance": function() {

					var bValid = true;
					allFields.removeClass( "ui-state-error" ); 	// Remove UI validation flags

					bValid = bValid && checkLength( name, "image_name", 3, 16 );	// Validate image_name length

					// If instance parameters are valid, proceed with instance generation
					if ( bValid ) {	

						message.showMessage('notice', 'Creating New Instance ' + name.val());	// Flag notice

                        if ($('#delete-instance').is(':visible')) { $('#delete-instance').toggle(); }
                        if ($('#create-instance').is(':visible')) { $('#create-instance').toggle(); }

                        $('.disable-action').bind('click', false);
                        var origActionColor = $('.disable-action').css('color');
                        $('.disable-action').css('color', '#696969');
						
						// Initialize progressbar and make it visible if hidden
						$('#instance_progressbar').progressbar({value: false});
						if ($('#instance_progressbar').is(':hidden')) {	$('#instance_progressbar').toggle(); };

						$.getJSON('/create_image/' + name.val() + '/' + sec_group_name.val() + '/nova/' + flavor_name.val() + '/' + sec_key_name.val() + '/' + image_name.val() + '/' + network_name.val() + '/' + PROJECT_ID + '/')
						.success(function(data){

							// Check if instance was successfully generated
							if(data.status == 'error'){message.showMessage('error', data.message); };	// Flag error message
							if(data.status == 'success'){												// Update interface

								message.showMessage('success', data.message);	// Flag success message

								var newRow = '';								// Initialize empty string for new instance row

								// --- BEGIN html string generation
								// Start row
								newRow += '<tr id="'+data.server_info.server_id+'">';
								// Create name-cell
								newRow += '<td id="'+data.server_info.server_id+'-name-cell"><a href="/'+PROJECT_ID+'/'+data.server_info.server_id+'/instance_view/" class="disable-instance-action"><span id="'+data.server_info.server_id+'-name-text">'+data.server_info.server_name+'</span></a></td>';
								// Create status-cell
								newRow += '<td id="'+data.server_info.server_id+'-status-cell">'+data.server_info.server_status+'</td>';
								// Create os-cell
								newRow += '<td id="'+data.server_info.server_id+'-os-cell">'+data.server_info.server_os+' / '+data.server_info.server_flavor+'</td>';
								// Start actions-cell
								newRow += '<td id="'+data.server_info.server_id+'-actions-cell">';
								// Populate actions-cell
								if(data.server_info.server_status == "ACTIVE"){
									newRow += '<a href="'+data.server_info.novnc_console+'" target="_blank">console</a><span class="instance-actions-pipe"> | </span><a href="#" class="pause-instance">pause</a><span class="instance-actions-pipe"> | </span><a href="#" class="suspend-instance">suspend</a>';
								};
								if(data.server_info.server_status == "PAUSED"){
									newRow += '<a href="#" class="unpause-instance">unpause</a>';
								};
								if(data.server_info.server_status == "SUSPENDED"){
									newRow += '<a href="#" class="resume-instance">resume</a>';
								};
								// End actions-cell and row
								newRow += '</td></tr>';
								// --- END html string generation

								// Check to see if this is the first instance to be generated, if so remove placeholder and reveal delete-instance button
								var rowCount = $('#instance_list tr').length;
								if (rowCount <= 2) {
									$('#instance_placeholder').remove().fadeOut();
									if ($('#delete-instance').is(':hidden')) { $('#delete-instance').toggle(); };
								};

								// Append new row to instance-list
								$('#instance_list').append(newRow).fadeIn();	

								// Create a new option for the new instance								
								var newOption = '<option value='+data.server_info.server_id+'>'+data.server_info.server_name+'</option>';

								// Append new option to delete-instance select menu 
								var deleteSelect = 'div#instance-delete-dialog-form > form > fieldset > select#instance';
								$(deleteSelect).append(newOption);

								// Append new option to attach-volume select menu
								var attachSelect = 'div#volume-attach-dialog-form > form  > fieldset > select#instance';
								$(attachSelect).append(newOption);

                                //
                                var assignSelect = 'div#fip-assign-dialog-form > form > fieldset > select#assign_instance';
                                $(assignSelect).append(newOption);
							};

							// Hide progressbar on completion
							if ($('#instance_progressbar').is(':visible')) { $('#instance_progressbar').toggle(); };

                            if ($('#delete-instance').is(':hidden')) { $('#delete-instance').toggle(); }
                            if ($('#create-instance').is(':hidden')) { $('#create-instance').toggle(); }
                            $('.disable-action').unbind('click', false);
                            $('.disable-action').css('color', origActionColor);

                        })
						.error(function(){

							message.showMessage('error', 'Server Fault');	// Flage server fault message

							// Hide progressbar on error		
							if ($('#instance_progressbar').is(':visible')) { $('#instance_progressbar').toggle(); }

                            if ($('#delete-instance').is(':hidden')) { $('#delete-instance').toggle(); }
                            if ($('#create-instance').is(':hidden')) { $('#create-instance').toggle(); }
                            $('.disable-action').unbind('click', false);
                            $('.disable-action').css('color', origActionColor);
                        });

					$( this ).dialog( "close" );	// Close modal form	
					}
				},
				Cancel: function() { $( this ).dialog( "close" ); }	// Close modal form				
			},
			close: function() {	allFields.val( "" ).removeClass( "ui-state-error" ); }	// Remove ui validations			
		})

		// Open modal form when create-instance button clicked
		$( "#create-instance" ).click(function() { $( "#instance-dialog-form" ).dialog( "open" ); });
	});
});
