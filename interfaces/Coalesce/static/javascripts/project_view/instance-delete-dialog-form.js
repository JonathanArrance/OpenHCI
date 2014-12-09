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

                    if ($('#delete-instance').is(':visible')) { $('#delete-instance').toggle(); }
                    if ($('#create-instance').is(':visible')) { $('#create-instance').toggle(); }

                    $('.disable-action').bind('click', false);
                    var origActionColor = $('.disable-action').css('color');
                    $('.disable-action').css('color', '#696969');

                    var confirmedInstance = instance.val();
                    var confirmedInstanceName = instance;

					// Initialize progressbar and make it visible if hidden
					$('#instance_progressbar').progressbar({value: false});
					if ($('#instance_progressbar').is(':hidden')) {	$('#instance_progressbar').toggle(); };

					$.getJSON('/server/' + PROJECT_ID + '/' + confirmedInstance + '/delete_server/')
						.success(function(data){

							// Check if instance was successfully deleted
                        	if(data.status == 'error'){ message.showMessage('error', data.message); }; 	// Flag error message 
                        	if(data.status == 'success'){ 												// Update interface

                        		message.showMessage('success', data.message);	// Flag success message

                        		// Remove instance row from instance_list
                        		var targetRow = '#' + confirmedInstance;
                        		$('#instance_list').find(targetRow).fadeOut().remove();

                        		// Remove instance from delete-instance select menu
                        		var deleteSelect = 'div#instance-delete-dialog-form > form > fieldset > select#instance option[value='+confirmedInstance+']';
                        		$(deleteSelect).remove();

                                // Remove instance from attach-volume select menu
                                var attachSelect = 'div#volume-attach-dialog-form > form  > fieldset > select#instance option[value='+confirmedInstance+']';
                                $(attachSelect).remove();

                                // Remove instance from assign-fip select menu
                                var assignSelect = 'div#fip-assign-dialog-form > form > fieldset > select#assign_instance option[value='+confirmedInstance+']';
                                $(assignSelect).remove();

                                for(var i=0; i < data.vols.length; i++) {
                                    var volAttachedCell = document.getElementById(data.vols[i]+'-attached-cell');
                                    $(volAttachedCell).empty().fadeOut();
                                    var newAttached = '<span id="'+data.vols[i]+'-attached-placeholder">No Attached Instance</span>';
                                    $(volAttachedCell).append(newAttached).fadeIn();

                                    var volActionsCell = document.getElementById(data.vols[i]+'-actions-cell');
                                    $(volActionsCell).empty().fadeOut();
                                    var newVolAction = '<a href="#" class="attach-instance">attach</a>';
                                    $(volActionsCell).append(newVolAction).fadeIn();
                                }

                                for(var j=0; j < data.floating_ip.length; j++) {
                                    var ipInstanceCell = document.getElementById(data.floating_ip[j]+'-instance-cell');
                                    $(ipInstanceCell).empty().fadeOut();
                                    var newInstance = '<span id="'+data.floating_ip[j]+'-instance-name">None</span>';
                                    $(ipInstanceCell).append(newInstance).fadeIn();

                                    var ipActionsCell = document.getElementById(data.floating_ip[j]+'-actions-cell');
                                    $(ipActionsCell).empty().fadeOut();
                                    var newIpAction = '<a id="'+data.floating_ip[j]+'" class="deallocate_ip" href="#">deallocate</a>';
                                    $(ipActionsCell).append(newIpAction).fadeIn();
                                }

                        		// Hide progressbar on completion
                        		if ($('#instance_progressbar').is(':visible')) { $('#instance_progressbar').toggle(); };

                                if ($('#delete-instance').is(':hidden')) { $('#delete-instance').toggle(); }
                                if ($('#create-instance').is(':hidden')) { $('#create-instance').toggle(); }
                                $('.disable-action').unbind('click', false);
                                $('.disable-action').css('color', origActionColor);

                                // Check to see if this is the last instance, if so add a placeholder row and hide delete-instance button
                                var rowCount = $('#instance_list tr').length;
                                if (rowCount < 2) {
                                    var placeholder = '<tr id="instance_placeholder"><td><p><i>This project has no instances</i></p></td><td></td><td></td><td></td></tr>';
                                    $('#instance_list').append(placeholder).fadeIn();
                                    if ($('#delete-instance').is(':visible')) {	$('#delete-instance').toggle();	};
                                }
                            }
                        })
						.error(function(){

							message.showMessage('error', 'Server Fault');	// Flag server fault message

							// Hide progressbar on error
							if ($('#instance_progressbar').is(':visible')) { $('#instance_progressbar').toggle(); };

                            if ($('#delete-instance').is(':hidden')) { $('#delete-instance').toggle(); }
                            if ($('#create-instance').is(':hidden')) { $('#create-instance').toggle(); }
                            $('.disable-action').unbind('click', false);
                            $('.disable-action').css('color', origActionColor);
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
