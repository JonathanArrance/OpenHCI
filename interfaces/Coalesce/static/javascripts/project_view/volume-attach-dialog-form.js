$(function() {

	var message = new message_handle();	// Initialize message handling
	var volumeId = '';					// Initialize empty string to hold ID of clicked volume

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

		var instance = $( "#instance" ),
			tips = $( ".validateTips" );

		function updateTips( t ) {
			tips.text( t ).addClass( "ui-state-highlight" );
			setTimeout(function() { tips.removeClass( "ui-state-highlight", 1500 ); }, 500 );
		}

		$( "#volume-attach-dialog-form" ).dialog({
			autoOpen: false,
			height: 400,
			width: 350,
			modal: true,
			buttons: {
				"Attach Volume": function() {

					var confirmedId = volumeId;														// Initialize string to hold ID of confirmed instance

					var confirmedNameSelector = '#'+confirmedId+'-name-text';						// Create string to target confirmed volume name-cell
					var confirmedName = $('#volume_list').find(confirmedNameSelector).text();		// Find confirmed volume name

					// Get Id of selected instance
					var confirmedInstance = $('div#volume-attach-dialog-form > form  > fieldset > select#instance option:selected').val();

					var selectedNameSelector = '#'+confirmedInstance+'-name-text';					// Create string to target selected instance
					var selectedName = $('#instance_list').find(selectedNameSelector).text();		// Find selected instance name

					var noticeMessage = 'Attaching volume '+confirmedName+' to '+selectedName;		// Create notice message
					console.log(noticeMessage);	// DEBUG
					message.showMessage('notice', noticeMessage);									// Flag notice message

					// --- BEGIN Create loader
					// Target clicked action link
					var confirmedActionSelector = '#'+confirmedId+'-actions-cell > .attach-instance';

					console.log(confirmedActionSelector);

					var confirmedActionHtml = '<a href="#" class="attach-instance">attach</a>';		// Copy the html that link
					var loaderId = confirmedId+'-loader';											// Target new loader ID
					var loaderHtml = '<div class="ajax-loader" id="'+loaderId+'"></div>';			// New loader html

					// Clear clicked action link and replace with loader
					$(confirmedActionSelector).empty().fadeOut();
					$(confirmedActionSelector).append(loaderHtml).fadeIn();
					loaderId = '#'+loaderId;														// Update loader ID
					// --- END Create Loader

					$.getJSON('/attach_volume/' + PROJECT_ID + '/' + confirmedInstance + '/' + volumeId)
					.success(function(data){ 

							// Check if instance was successfully paused
                        	if(data.status == 'error'){ 
                        		message.showMessage('error', data.message);									// Flag error message

                        		// Recall clicked action link on error
                        		$(confirmedActionSelector).empty().fadeOut();							
                        		$(confirmedActionSelector).append(confirmedActionHtml).fadeIn();
                        	}

                       		 if(data.status == 'success'){ 													// Update interface

                        		message.showMessage('success', data.message);							// Flag success message

                        		var actionsSelector = '#'+confirmedId+'-actions-cell';					// Target instance-actions-cell

                        		var detachAction = '<a href="#" class="detach-instance">detach</a>';	// New actions html string

                        		// Update action cell							
                        		$(actionsSelector).fadeOut().empty();
                        		$(actionsSelector).append(detachAction).fadeIn();
                        	}
                        })
                        .error(function(){

							message.showMessage('error', 'Server Fault'); 									// Flag server fault message

							// Recall clicked action link on server fault
							$(confirmedActionSelector).empty().fadeOut();
							$(confirmedActionSelector).append(confirmedActionHtml).fadeIn();

					});

					$( this ).dialog( "close" );					// Close Modal Form
				},
				Cancel: function() { $( this ).dialog( "close" ); }	// Close Modal Form
			},
			close: function() {	}
		})

		// Open modal form when attach-instance button clicked
		$(document).on('click', '.attach-instance', function(){

			volumeId = $(this).parent().parent().attr('id');		// Get the ID of the instance that the user wishes to attach
						
			// Clear and add volume name to .volume-name span in confirm statement
			var nameSelector = '#'+volumeId+'-name-text';
			$('#volume-attach-dialog-form > p > span.volume-name')
				.empty()
				.append($(nameSelector).text());

			$( "#volume-attach-dialog-form" ).dialog( "open" ); 	// Open Pause Confirm Form	
		});
	});
});
